# AI-Powered Applicant Tracking System (ATS)

An AI-driven evaluation tool that matches PDF resumes with job descriptions using Groq's Llama 3.3 model. It automates JD scraping, calculates match percentages, and identifies skill gaps to help candidates optimize their profiles for competitive tech roles.

## Key Features
- **Resume Analysis**: Extracts text from PDF resumes and evaluates them against a job description.
- **JD Scraping**: Scrapes job descriptions directly from URLs using BeautifulSoup.
- **LLM Integration**: Leverages Groq (Llama 3.3 70B) for high-accuracy matching and feedback.
- **Detailed Feedback**: Provides JD match percentage, missing keywords, and profile summaries.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt` (Note: Create a requirements.txt if not present).
3. Set up your `.env` file with `GROQ_API_KEY`.
4. Run the application: `python ATS.py`.
