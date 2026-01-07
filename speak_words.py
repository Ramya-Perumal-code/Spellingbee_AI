import sqlite3
import torch
from transformers import AutoProcessor, BarkModel
import scipy.io.wavfile
import os

# Configuration
DB_FILE = 'my_database.db'
TABLE_NAME = 'bee_words'
OUTPUT_DIR = 'audio_output'

def setup_model():
    """Load the Bark model and processor."""
    print("Loading Bark model... (this may take a moment)")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoProcessor.from_pretrained("suno/bark")
    model = BarkModel.from_pretrained("suno/bark").to(device)
    print(f"Model loaded on {device}.")
    return processor, model, device

def generate_audio(text, processor, model, device, filename):
    """Generate audio for a given text and save it."""
    inputs = processor(text, voice_preset="v2/en_speaker_6").to(device)
    
    with torch.no_grad():
        # pad_token_id=10000 avoids the warning
        audio_array = model.generate(**inputs, pad_token_id=10000)
    
    audio_array = audio_array.cpu().numpy().squeeze()
    
    # Bark generates at 24kHz
    sample_rate = 24000
    scipy.io.wavfile.write(filename, sample_rate, audio_array)
    print(f"Saved: {filename}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Connect to Database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get the first column (assuming it contains the words)
    cursor.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 5") # Limiting to 5 for testing
    rows = cursor.fetchall()
    
    if not rows:
        print("No data found in database.")
        return

    # 2. Setup TTS Model
    try:
        processor, model, device = setup_model()
    except Exception as e:
        print(f"Failed to load model. Ensure transformers and torch are installed.\nError: {e}")
        return

    # 3. Process Words
    print("Generating audio for the first 5 entries...")
    for i, row in enumerate(rows):
        # Assuming the first element of the tuple is the text
        text = str(row[0]).strip()
        if not text:
            continue
            
        # Clean text slightly if needed
        clean_text = text.replace('**', '').replace('  ', ' ').strip()
        
        filename = os.path.join(OUTPUT_DIR, f"word_{i}_{clean_text[:10]}.wav")
        generate_audio(clean_text, processor, model, device, filename)

    print("Done!")
    conn.close()

if __name__ == "__main__":
    main()
