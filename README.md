# Research Assistant

A Streamlit-based research assistant that combines information from Wikipedia and recent news sources to provide comprehensive research results.

## Setup

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API keys:
```
GROQ_API_KEY=your_key_here

# Optional email settings
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_email_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

4. Get your Groq API key:
   - Create an account at https://groq.com/
   - Generate an API key
   - Add it to your `.env` file

## Running the App

Run the Streamlit app with:
```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`.

## Features

- 📚 Wikipedia research
- 📰 Real-time news aggregation
- 💡 Research suggestions
- 📊 Categorized results
- 🌐 Multiple news sources

## Usage

1. Enter your research topic in the search box
2. View the comprehensive summary
3. Explore recent news by category
4. Check sources and research tips 