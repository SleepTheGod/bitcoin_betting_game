from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# In-memory "database" for simplicity
users = {}
bets = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    user_address = data.get('address')
    
    if user_address in users:
        return jsonify({'message': 'User already exists'}), 400
    users[user_address] = {'balance': 0.0}
    
    return jsonify({'message': 'User created successfully'})

@app.route('/place_bet', methods=['POST'])
def place_bet():
    data = request.get_json()
    user_id = data.get('user_id')
    bet_amount = data.get('amount')
    
    if not user_id or user_id not in users:
        return jsonify({'message': 'User not found'}), 400
    if bet_amount <= 0:
        return jsonify({'message': 'Invalid bet amount'}), 400
    
    # Mock multiplier
    multiplier = 1.5
    
    # Update user's balance
    if user_id not in bets:
        bets[user_id] = []
    
    bets[user_id].append({'amount': bet_amount, 'multiplier': multiplier})
    
    return jsonify({'multiplier': multiplier})

if __name__ == '__main__':
    app.run(debug=True)
