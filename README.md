# Agentic AI Spelling Bee

An interactive, voice-controlled Spelling Bee game powered by AI. This application uses Flask for the web interface, Google Speech Recognition for voice input, and Groq's Llama 3.3 model to provide rich context (definitions, origins, and example sentences) for each word.

## 🚀 Features

- **Voice-First Interaction**: Uses Speech-to-Text (STT) for spelling attempts and commands.
- **AI-Powered Hints**: Leverages Groq (Llama 3.3 70B) to provide word meanings, origins, and example sentences.
- **Dynamic Word Lists**: Syncs words from an Excel file (`word_list.xlsx`) into a local SQLite database.
- **Filtering & Metadata**: Filter words by Year, List, or Difficulty.
- **Text-to-Speech (TTS)**: Built-in synthesis using PowerShell for audio feedback.
- **Real-time Evaluation**: Automatically extracts and verifies spelling attempts from voice input.

## 🛠️ Project Structure

- `app.py`: Flask web server and API endpoints.
- `spelling_bee.py`: Core game logic, STT/TTS integration, and LLM context fetching.
- `my_database.db`: SQLite database storing words and metadata.
- `word_list.xlsx`: Source file for word data.
- `templates/index.html`: Web interface for the game.

## ⚙️ Setup

### Prerequisites
- **Python 3.8+**
- **Windows OS** (required for PowerShell-based TTS)
- **Microphone** (for voice interaction)
- **Groq API Key**

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install flask sounddevice scipy numpy speechrecognition pandas openpyxl groq python-dotenv
   ```
3. Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

### Database Initialization
The game automatically syncs data from `word_list.xlsx` to the database on startup. Ensure `word_list.xlsx` follows a standard column format (Word, Year, Difficulty, List).

## 🎮 How to Play

1. Run the application:
   ```bash
   python app.py
   ```
2. Open your browser to `http://127.0.0.1:5000`.
3. Use the interface to set filters or order (Random/Alphabetical).
4. **Voice Commands**:
   - "Repeat the word" or "Say the word again"
   - "What is the meaning?" or "Give me a hint"
   - "Give me the origin"
   - "Use it in a sentence"
   - "Pause" or "Stop"
5. To spell a word, simply speak it clearly. The system is designed to handle "Word [S-P-E-L-L-I-N-G] Word" format automatically.

## 📝 License
MIT
