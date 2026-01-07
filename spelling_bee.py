import sounddevice as sd
import subprocess
import scipy.io.wavfile as wav
import numpy as np
import os
import sqlite3
import random
import time
import speech_recognition as sr


from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configuration
DB_FILE = 'my_database.db'
TABLE_NAME = 'bee_words'
TEMP_WAV = 'temp_recording.wav'
SAMPLE_RATE = 44100
DURATION = 10 

class SpellingBeeGame:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.words = []
        self.current_word = None
        self.score = {'correct': 0, 'incorrect': 0}
        
        # Setup Groq
        if GROQ_API_KEY:
            self.client = Groq(api_key=GROQ_API_KEY)
        else:
            self.client = None
            print("Warning: GROQ_API_KEY not found in .env file.")
            
        self.load_words()

    def get_context(self, word):
        if not self.client:
            return "Groq API key not configured."
            
        try:
            prompt = f"Provide the definition, part of speech, and one example sentence for the word '{word}'. " \
                     f"Mask the word '{word}' in the definition and example sentence with '***'. " \
                     f"Format: '(part of speech) definition | Ex: example sentence'. " \
                     f"Be extremely concise. Do not include any other text."
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content.strip()
                        
        except Exception as e:
            print(f"Groq API Error: {e}")
            
        return "No definition available."

    def load_words(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_NAME}")
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                self.words = [str(row[0]).strip().replace('**', '').replace('  ', ' ').strip() for row in rows if row[0]]
                random.shuffle(self.words)
                print(f"Loaded {len(self.words)} words.")
            else:
                print("No words found in DB.")
                
        except Exception as e:
            print(f"Database error: {e}")

    def get_next_word(self):
        if not self.words:
            return None
        self.current_word = self.words.pop(0)
        # Put it back at the end? or just consume? consuming for now.
        self.words.append(self.current_word) 
        return self.current_word

    def speak(self, text):
        print(f"Agent: {text}")
        safe_text = text.replace("'", "''")
        command = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_text}');"
        subprocess.run(["powershell", "-Command", command], shell=False)

    def listen_and_recognize(self, duration=DURATION):
        if os.path.exists(TEMP_WAV):
            try:
                os.remove(TEMP_WAV)
            except: pass

        print(f"Listening for {duration} seconds...")
        
        try:
            # Record
            my_recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
            sd.wait()
            wav.write(TEMP_WAV, SAMPLE_RATE, my_recording)
            
            # Recognize
            recognizer = sr.Recognizer()
            with sr.AudioFile(TEMP_WAV) as source:
                audio = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio)
                    return text
                except sr.UnknownValueError:
                    return None
                except sr.RequestError:
                    return "ERROR: Network/API"
        except Exception as e:
            print(f"Recording Error: {e}")
            return "ERROR: Recording"
        finally:
             if os.path.exists(TEMP_WAV):
                try:
                    os.remove(TEMP_WAV)
                except: pass

    def check_spelling(self, user_input, target_word):
        if not user_input: return False
        clean_input = user_input.replace(" ", "").lower()
        clean_target = target_word.lower().replace(" ", "")
        
        is_correct = (clean_input == clean_target)
        if is_correct:
            self.score['correct'] += 1
        else:
            self.score['incorrect'] += 1
            
        return is_correct

def main():
    game = SpellingBeeGame()
    while True:
        word = game.get_next_word()
        if not word: break
        
        game.speak(f"The word is {word}")
        context = game.get_context(word)
        print(f"Hint: {context}")
        time.sleep(0.5)
        game.speak(f"Please spell {word}")
        
        user_text = game.listen_and_recognize()
        if user_text:
            game.speak(f"You said: {user_text}")
            if game.check_spelling(user_text, word):
                game.speak(f"Correct! The word is {word}.")
            else:
                game.speak(f"Incorrect. The word is {word}.")
        else:
            game.speak("I didn't hear anything.")
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
