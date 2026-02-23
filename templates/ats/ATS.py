import os
import PyPDF2 as pdf
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, jsonify
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configure Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_groq_response(resume_text, jd, prompt_template):
    # Combine the prompt with the data
    full_prompt = prompt_template.format(text=resume_text, jd=jd)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": full_prompt,
            }
        ],
        model="llama-3.3-70b-versatile", # High performance Llama model
    )
    return chat_completion.choices[0].message.content

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page_obj = reader.pages[page]
        text += str(page_obj.extract_text())
    return text

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and the missing keywords with high accuracy.

resume: {text}
description: {jd}

I want the response in a VALID JSON format. Do not include any conversational text or markdown blocks unless it's the JSON itself.
The structure must be:
{{
  "JD Match": "XX%",
  "MissingKeywords": ["list", "of", "words"],
  "Profile Summary": "Detailed summary here",
  "SkillsMatching": [
    {{"skill": "Python", "score": 90}},
    {{"skill": "Machine Learning", "score": 60}},
    {{"skill": "SQL", "score": 85}}
  ]
}}
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text
        text = soup.get_text()
        
        # Breakdown into lines and remove leading/trailing whitespace
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return jsonify({"text": clean_text[:5000]}) # Limit to roughly 5000 chars for prompt safety
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    jd = request.form['jd']
    uploaded_files = request.files.getlist('resume')

    if not uploaded_files or not jd:
        return jsonify({"error": "Missing files or JD"}), 400

    results = []
    for uploaded_file in uploaded_files:
        if uploaded_file.filename == '':
            continue
            
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                text = input_pdf_text(f)
            
            # Get Groq Analysis
            response_text = get_groq_response(text, jd, input_prompt)
            results.append({
                "filename": uploaded_file.filename,
                "analysis": response_text
            })
        except Exception as e:
            results.append({
                "filename": uploaded_file.filename,
                "error": str(e)
            })
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
