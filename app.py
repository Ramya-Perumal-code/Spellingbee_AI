from flask import Flask, render_template, jsonify
from spelling_bee import SpellingBeeGame
import threading

app = Flask(__name__)
game = SpellingBeeGame()

# Store current word and details in memory for the session
current_word = None
current_details = None
speech_lock = threading.Lock()

def speak_async(text):
    """Speaks text in a background thread to avoid blocking the web response."""
    # Acquire lock in main thread immediately to prevent listener from jumping in
    speech_lock.acquire()
    def run_speech():
        try:
            game.speak(text)
        finally:
            speech_lock.release()
    threading.Thread(target=run_speech, daemon=True).start()

@app.route('/api/wait_for_speech', methods=['GET'])
def wait_for_speech():
    """Blocks until any ongoing speech is finished."""
    with speech_lock:
        pass
    return jsonify({'status': 'done'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/started', methods=['GET'])
def check_started():
    # Just a handshake
    return jsonify({'status': 'ok'})

@app.route('/api/next_word', methods=['POST'])
def next_word():
    global current_word, current_details
    current_word = game.get_next_word()
    if current_word:
        # Get context (meaning, origin, sentence)
        current_details = game.get_context(current_word)
        
        # Speak the word on the server
        speak_async(f"The word is {current_word}. Please spell {current_word}")
        
        return jsonify({
            'word': current_word, 
            'status': 'spoken',
            'score': game.score
        })
    else:
        return jsonify({'error': 'No words left'}), 404

@app.route('/api/repeat_word', methods=['POST'])
def repeat_word():
    global current_word
    if current_word:
        speak_async(f"Please spell {current_word}")
        return jsonify({'status': 'repeated'})
    return jsonify({'error': 'No active word'}), 400

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Returns unique Year, List, and Difficulty options for metadata."""
    return jsonify(game.get_filter_metadata())

@app.route('/api/update_filters', methods=['POST'])
def update_filters():
    """Updates the game word filters (Year, List, Difficulty)."""
    from flask import request
    data = request.json
    game.set_filters(
        year=data.get('year'),
        list_type=data.get('list'),
        difficulty=data.get('difficulty')
    )
    return jsonify({
        'status': 'ok',
        'word_count': len(game.words),
        'filters': game.filters
    })

@app.route('/api/set_order', methods=['POST'])
def set_order():
    from flask import request
    data = request.json
    order = data.get('order', 'random')
    game.set_order(order)
    return jsonify({'status': 'ok', 'order': order})

@app.route('/api/listen', methods=['POST'])
def listen():
    global current_word, current_details
    if not current_word:
         return jsonify({'error': 'No active word'}), 400
         
    # Wait for any ongoing speech to finish before listening
    with speech_lock:
        user_text = game.listen_and_recognize()
    
    if user_text:
        text_lower = user_text.lower()
        print(f"Debug - Heard: '{user_text}'")
        
        # Check for hint keywords
        if "meaning" in text_lower or "definition" in text_lower:
            hint = current_details.get('meaning', 'No meaning available.')
            speak_async(f"The meaning is: {hint}")
            return jsonify({'result': 'hint', 'type': 'meaning', 'text': hint})
        
        elif "origin" in text_lower or "root" in text_lower:
            hint = current_details.get('origin', 'No origin available.')
            speak_async(f"The origin is: {hint}")
            return jsonify({'result': 'hint', 'type': 'origin', 'text': hint})
            
        elif "sentence" in text_lower or "example" in text_lower:
            hint = current_details.get('sentence', 'No example sentence available.')
            speak_async(f"The sentence is: {hint}")
            return jsonify({'result': 'hint', 'type': 'sentence', 'text': hint})

        # 1. Check for Pause/Stop (highest priority)
        if any(kw in text_lower for kw in ["pause", "stop", "wait", "hold on"]):
            print(f"Debug - Pause triggered by: '{text_lower}'")
            speak_async("Pausing. Click Resume to continue.")
            return jsonify({'result': 'paused'})

        # 2. Check for Standalone Commands (pure instructions)
        command_kws = ["repeat", "word again", "say the word again", "say the word", "repeat the word", "repeat word", "the word"]
        clean_text = text_lower.replace("please", "").replace("can you", "").strip()
        
        if any(clean_text == kw for kw in command_kws):
            speak_async(f"The word is {current_word}. Please spell {current_word}")
            return jsonify({'result': 'hint', 'type': 'repeat', 'text': f"Repeating: {current_word}"})

        # 3. Robust Extraction for "Word [Spelling] Word" format
        target = current_word.lower().strip()
        # Remove target word from start and end if present
        # We use split/join to handle words that might appear multiple times or as part of others
        words_heard = text_lower.split()
        
        # Try to find the target word at the very beginning and very end
        start_idx = 0
        end_idx = len(words_heard)
        
        if words_heard and words_heard[0] == target:
            start_idx = 1
        if len(words_heard) > 1 and words_heard[-1] == target:
            end_idx = len(words_heard) - 1
            
        # The content in between is the spelling attempt
        spelling_attempt = "".join(words_heard[start_idx:end_idx])
        
        # If extraction left us with nothing, but user said something, 
        # it might just be the word itself (repeat request)
        if not spelling_attempt and len(words_heard) > 0:
            speak_async(f"The word is {current_word}. Please spell {current_word}")
            return jsonify({'result': 'hint', 'type': 'repeat', 'text': f"Repeating: {current_word}"})

        # Validate the extracted spelling
        print(f"Debug - Extracted Spelling: '{spelling_attempt}'")
        is_correct = game.check_spelling(spelling_attempt, current_word)
        
        if is_correct:
            speak_async(f"Correct! The word is {current_word}.")
            return jsonify({
                'result': 'correct', 
                'heard': " ".join(words_heard[start_idx:end_idx]), # Return spaced for UI
                'target': current_word,
                'score': game.score
            })
        else:
            speak_async(f"Incorrect. The word is {current_word}.")
            return jsonify({
                'result': 'incorrect', 
                'heard': " ".join(words_heard[start_idx:end_idx]), 
                'target': current_word,
                'score': game.score
            })
            
    else:
        print("Debug - No voice input detected.")
        speak_async("I didn't hear anything.")
        return jsonify({'result': 'no_input', 'target': current_word})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
