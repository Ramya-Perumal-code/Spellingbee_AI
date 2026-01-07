from flask import Flask, render_template, jsonify
from spelling_bee import SpellingBeeGame
import threading

app = Flask(__name__)
game = SpellingBeeGame()

# Store current word in memory for the session
current_word = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/started', methods=['GET'])
def check_started():
    # Just a handshake
    return jsonify({'status': 'ok'})

@app.route('/api/next_word', methods=['POST'])
def next_word():
    global current_word
    current_word = game.get_next_word()
    if current_word:
        # Get context
        definition = game.get_context(current_word)
        
        # Speak the word on the server
        game.speak(f"The word is {current_word}")
        # Small delay handled by frontend or separate call? 
        # For simplicity, speak both parts here
        game.speak(f"Please spell {current_word}")
        return jsonify({
            'word': current_word, 
            'status': 'spoken',
            'definition': definition,
            'score': game.score
        })
    else:
        return jsonify({'error': 'No words left'}), 404

@app.route('/api/listen', methods=['POST'])
def listen():
    global current_word
    if not current_word:
         return jsonify({'error': 'No active word'}), 400
         
    # This blocks the server! But for a single user local app, it's fine.
    user_text = game.listen_and_recognize()
    
    if user_text:
        game.speak(f"You said: {user_text}")
        is_correct = game.check_spelling(user_text, current_word)
        if is_correct:
             game.speak(f"Correct! The word is {current_word}.")
             return jsonify({
                 'result': 'correct', 
                 'heard': user_text, 
                 'target': current_word,
                 'score': game.score
             })
        else:
             game.speak(f"Incorrect. The word is {current_word}.")
             return jsonify({
                 'result': 'incorrect', 
                 'heard': user_text, 
                 'target': current_word,
                 'score': game.score
             })
    else:
        game.speak("I didn't hear anything.")
        return jsonify({'result': 'no_input', 'target': current_word})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
