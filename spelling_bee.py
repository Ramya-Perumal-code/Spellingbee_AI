import sounddevice as sd
import subprocess
import scipy.io.wavfile as wav
import numpy as np
import os
import sqlite3
import random
import time
import speech_recognition as sr
import queue
import pandas as pd


from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configuration
DB_FILE = 'my_database.db'
TABLE_NAME = 'bee_words'
EXCEL_FILE = 'word_list.xlsx'
TEMP_WAV = 'temp_recording.wav'
SAMPLE_RATE = 44100
DURATION = 10 

class SpellingBeeGame:
    def __init__(self, db_file=DB_FILE, order='random'):
        self.db_file = db_file
        self.words = []
        self.current_word = None
        self.score = {'correct': 0, 'incorrect': 0}
        self.order = order
        self.filters = {'year': None, 'list': None, 'difficulty': None}
        
        # Setup Groq
        if GROQ_API_KEY:
            self.client = Groq(api_key=GROQ_API_KEY)
        else:
            self.client = None
            print("Warning: GROQ_API_KEY not found in .env file.")
            
        # Sync database with Excel if it exists
        if os.path.exists(EXCEL_FILE):
            self.sync_excel_to_db(EXCEL_FILE)
            
        self.load_words()

    def sync_excel_to_db(self, excel_path):
        """Standardizes and syncs Excel data to the SQLite database."""
        try:
            print(f"Syncing {excel_path} to database...")
            df = pd.read_excel(excel_path)
            
            # Fuzzy match column names
            col_map = {}
            for col in df.columns:
                c_clean = str(col).strip().lower()
                if 'word' in c_clean: col_map['word'] = col
                elif 'year' in c_clean: col_map['year'] = col
                elif 'difficulty' in c_clean or 'level' in c_clean: col_map['difficulty'] = col
                elif 'list' in c_clean: col_map['list'] = col
            
            print(f"Detected columns: {col_map}")
            
            # Map required columns
            data_to_store = pd.DataFrame()
            if 'word' in col_map:
                data_to_store['word'] = df[col_map['word']].astype(str).str.strip()
            if 'year' in col_map:
                data_to_store['year'] = df[col_map['year']].astype(str).str.strip()
            if 'difficulty' in col_map:
                data_to_store['difficulty'] = df[col_map['difficulty']].astype(str).str.strip()
            if 'list' in col_map:
                data_to_store['list'] = df[col_map['list']].astype(str).str.strip()
            
            # Drop empty words and 'nan' strings
            if 'word' in data_to_store:
                data_to_store = data_to_store[data_to_store['word'].str.lower() != 'nan']
                data_to_store = data_to_store[data_to_store['word'] != '']
            
            # Clean up 'nan' in other metadata columns
            for col in ['year', 'difficulty', 'list']:
                if col in data_to_store.columns:
                    data_to_store[col] = data_to_store[col].replace(['nan', 'None', ''], None)
            
            conn = sqlite3.connect(self.db_file)
            # Recreate table with proper schema
            conn.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
            conn.execute(f"""
                CREATE TABLE {TABLE_NAME} (
                    word TEXT,
                    year TEXT,
                    difficulty TEXT,
                    list TEXT
                )
            """)
            
            data_to_store.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
            conn.close()
            print(f"Sync complete. Stored {len(data_to_store)} words.")
            
        except Exception as e:
            print(f"Sync error: {e}")

    def set_filters(self, year=None, list_type=None, difficulty=None):
        self.filters = {
            'year': str(year) if year and str(year).lower() != 'all' else None,
            'list': str(list_type) if list_type and str(list_type).lower() != 'all' else None,
            'difficulty': str(difficulty) if difficulty and str(difficulty).lower() != 'all' else None
        }
        self.load_words()

    def get_filter_metadata(self):
        """Returns unique values for Year, List, and Difficulty from the DB."""
        metadata = {'years': [], 'lists': [], 'difficulties': []}
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT DISTINCT year FROM {TABLE_NAME} WHERE year IS NOT NULL AND year != 'None' AND year != 'nan' ORDER BY year DESC")
            metadata['years'] = [str(r[0]) for r in cursor.fetchall()]
            
            cursor.execute(f"SELECT DISTINCT list FROM {TABLE_NAME} WHERE list IS NOT NULL AND list != 'None' AND list != 'nan' ORDER BY list")
            metadata['lists'] = [str(r[0]) for r in cursor.fetchall()]
            
            cursor.execute(f"SELECT DISTINCT difficulty FROM {TABLE_NAME} WHERE difficulty IS NOT NULL AND difficulty != 'None' AND difficulty != 'nan' ORDER BY difficulty")
            metadata['difficulties'] = [str(r[0]) for r in cursor.fetchall()]
            
            conn.close()
        except Exception as e:
            print(f"Metadata error: {e}")
        return metadata

    def set_order(self, order):
        """Sets the word loading order ('random' or 'alphabetical')."""
        self.order = order
        self.load_words()

    def get_context(self, word):
        if not self.client:
            return {"meaning": "Groq API key not configured.", "origin": "N/A", "sentence": "N/A"}
            
        try:
            prompt = f"Provide the definition, origin/root, and one example sentence for the word '{word}'. " \
                     f"Mask the word '{word}' in the definition and example sentence with '***'. " \
                     f"Return the response ONLY as a JSON object with the following keys: 'meaning', 'origin', 'sentence'. " \
                     f"Do not include any other text or markdown formatting."
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            content = chat_completion.choices[0].message.content.strip()
            
            # Simple JSON parsing (removing possible markdown blocks if any)
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            import json
            details = json.loads(content)
            return {
                "meaning": details.get("meaning", "No definition available."),
                "origin": details.get("origin", "Origin unknown."),
                "sentence": details.get("sentence", "No example sentence available.")
            }
                        
        except Exception as e:
            print(f"Groq API Error: {e}")
            
        return {"meaning": "No definition available.", "origin": "Origin unknown.", "sentence": "No example sentence available."}

    def load_words(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            query = f"SELECT word FROM {TABLE_NAME} WHERE 1=1"
            params = []
            
            if self.filters['year']:
                query += " AND year = ?"
                params.append(self.filters['year'])
            if self.filters['list']:
                query += " AND list = ?"
                params.append(self.filters['list'])
            if self.filters['difficulty']:
                query += " AND difficulty = ?"
                params.append(self.filters['difficulty'])
                
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                all_words = [str(row[0]).strip().replace('**', '').replace('  ', ' ').strip() for row in rows if row[0]]
                self.words = [w for w in all_words if w and w.lower() != 'nan']
                
                if self.order == 'alphabetical':
                    self.words.sort()
                else:
                    random.shuffle(self.words)
                print(f"Loaded {len(self.words)} words with filters: {self.filters}")
            else:
                self.words = []
                print(f"No words found matching filters: {self.filters}")
                 
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
        recognizer = sr.Recognizer()
        print(f"Listening (Gapless, max {duration}s)...")
        
        q = queue.Queue()
        def callback(indata, frames, time_info, status):
            if status: print(f"Audio Status: {status}")
            q.put(indata.copy())

        audio_data = []
        silence_threshold = 80
        required_silence_duration = 2.0  # seconds of silence to trigger stop
        max_duration = duration
        
        has_started_speaking = False
        silence_duration = 0
        start_time = time.time()

        try:
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16', callback=callback):
                while time.time() - start_time < max_duration:
                    try:
                        # Get data from queue with short timeout to stay responsive
                        chunk = q.get(timeout=0.1)
                        audio_data.append(chunk)
                        
                        volume = np.abs(chunk).mean()
                        if volume > silence_threshold:
                            if not has_started_speaking:
                                print("Debug - Speech detected!")
                                has_started_speaking = True
                            silence_duration = 0
                        else:
                            if has_started_speaking:
                                # Calculate time based on chunk size
                                silence_duration += len(chunk) / SAMPLE_RATE
                        
                        if has_started_speaking and silence_duration >= required_silence_duration:
                            print("Silence detected, stopping recording.")
                            break
                    except queue.Empty:
                        continue
            
            if not audio_data: 
                return None
                
            # Combine chunks and save
            full_audio = np.concatenate(audio_data, axis=0)
            wav.write(TEMP_WAV, SAMPLE_RATE, full_audio)
            
            # Recognize using AudioFile
            with sr.AudioFile(TEMP_WAV) as source:
                audio = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio)
                    return text
                except sr.UnknownValueError:
                    return None
        except Exception as e:
            print(f"Gapless Listen Error: {e}")
            return None
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
