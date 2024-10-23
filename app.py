from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import random
import time
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app)

# In-memory databases for simplicity
users = {}
bets = {}
multiplier = 1.0
crash_point = None
game_running = False

# Function to simulate game rounds
def start_game():
    global multiplier, crash_point, game_running
    while True:
        time.sleep(5)  # Delay between rounds
        multiplier = 1.0
        crash_point = round(random.uniform(2.0, 10.0), 2)  # Random crash point
        game_running = True
        socketio.emit('new_round', {'multiplier': multiplier, 'crash_point': crash_point})

        while multiplier < crash_point:
            time.sleep(0.1)
            multiplier += 0.01
            socketio.emit('update_multiplier', {'multiplier': round(multiplier, 2)})
        
        game_running = False
        socketio.emit('crash', {'crash_point': crash_point})
        time.sleep(5)  # Pause after crash before next round

# Run the game loop in a separate thread
game_thread = Thread(target=start_game)
game_thread.daemon = True
game_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    user_address = data.get('address')
    
    if user_address in users:
        return jsonify({'message': 'User already exists'}), 400
    users[user_address] = {'balance': 100.0, 'bet': 0.0, 'in_game': False}
    
    return jsonify({'message': 'User created successfully'})

@app.route('/place_bet', methods=['POST'])
def place_bet():
    data = request.get_json()
    user_id = data.get('user_id')
    bet_amount = float(data.get('amount'))
    
    if not user_id or user_id not in users:
        return jsonify({'message': 'User not found'}), 400
    if bet_amount <= 0 or bet_amount > users[user_id]['balance']:
        return jsonify({'message': 'Invalid bet amount'}), 400
    
    users[user_id]['bet'] = bet_amount
    users[user_id]['balance'] -= bet_amount
    users[user_id]['in_game'] = True
    
    socketio.emit('bet_placed', {'user': user_id, 'amount': bet_amount, 'multiplier': round(multiplier, 2)})
    
    return jsonify({'message': 'Bet placed successfully'})

@app.route('/cash_out', methods=['POST'])
def cash_out():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id or user_id not in users:
        return jsonify({'message': 'User not found'}), 400
    if not users[user_id]['in_game']:
        return jsonify({'message': 'User is not in the game'}), 400
    
    cash_out_amount = users[user_id]['bet'] * multiplier
    users[user_id]['balance'] += cash_out_amount
    users[user_id]['bet'] = 0.0
    users[user_id]['in_game'] = False
    
    socketio.emit('user_cash_out', {'user': user_id, 'multiplier': round(multiplier, 2), 'cash_out_amount': round(cash_out_amount, 2)})
    
    return jsonify({'message': 'Cash out successful', 'balance': users[user_id]['balance']})

if __name__ == '__main__':
    socketio.run(app, debug=True)
