# AI Research Assistant

An intelligent research assistant that combines information from Wikipedia and recent news sources to provide comprehensive research results on any topic.

## Features

- Wikipedia information retrieval
- Real-time news integration via GNews API
- Email functionality to send research results
- Powered by Groq LLM for intelligent summarization

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   GROQ_API_KEY=your_groq_api_key
   GNEWS_API_KEY=your_gnews_api_key
   EMAIL_ADDRESS=your_email
   EMAIL_PASSWORD=your_email_password
   SMTP_SERVER=your_smtp_server
   SMTP_PORT=587
   ```

## Usage

Run the main script:
```bash
python main.py
```

Follow the prompts to enter your research query. The assistant will gather information from Wikipedia and recent news, then provide a comprehensive summary. 