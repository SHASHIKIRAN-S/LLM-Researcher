# AI Research Assistant 🔍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/yourusername/ai-research-assistant/graphs/commit-activity)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

<div align="center">
  <h1>AI Research Assistant</h1>
  <p>Your intelligent companion for comprehensive research and information gathering</p>
</div>

## 🎯 Overview

An advanced research assistant that leverages cutting-edge AI technology to provide comprehensive research results. By combining information from Wikipedia and real-time news sources, it delivers in-depth analysis and insights on any topic of interest.

### ✨ Key Features

- 🌐 **Smart Wikipedia Integration**
  - Intelligent information extraction
  - Context-aware content analysis
  - Automatic relevance filtering

- 📰 **Real-time News Analysis**
  - Live news integration via GNews API
  - Current events correlation
  - Trend analysis and insights

- 📧 **Automated Reporting**
  - Customizable email reports
  - Professional formatting
  - Scheduled delivery options

- 🧠 **AI-Powered Intelligence**
  - Powered by Groq LLM
  - Advanced text summarization
  - Natural language understanding

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for version control)
- Active internet connection

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/ai-research-assistant.git
   cd ai-research-assistant
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GNEWS_API_KEY=your_gnews_api_key
   EMAIL_ADDRESS=your_email
   EMAIL_PASSWORD=your_email_password
   SMTP_SERVER=your_smtp_server
   SMTP_PORT=587
   ```

## 💻 Usage Guide

1. **Start the Application**
   ```bash
   python main.py
   ```

2. **Research Process**
   - Enter your research topic when prompted
   - The assistant will:
     - Search Wikipedia for relevant information
     - Gather recent news articles
     - Analyze and synthesize the content
     - Generate a comprehensive summary

3. **Viewing Results**
   - Results are displayed in the terminal
   - Option to receive detailed report via email
   - Save results to PDF (optional)

## ⚙️ Configuration

Customize the assistant's behavior in `config.py`:

```python
{
    "wiki_results_limit": 5,
    "news_time_range": "7d",
    "summary_length": "medium",
    "email_format": "html"
}
```

## 📚 API Documentation

### Core Modules

#### Wikipedia Handler
```python
wiki.search(query: str) -> List[Article]
wiki.analyze(content: str) -> Summary
```

#### News Aggregator
```python
news.fetch(topic: str, days: int) -> List[Article]
news.process(articles: List[Article]) -> Analysis
```

#### Email Service
```python
email.format_report(content: dict) -> Template
email.send(recipient: str, report: Template) -> bool
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🔧 Troubleshooting

Common issues and solutions:

1. **API Connection Issues**
   - Verify API keys are valid
   - Check internet connection
   - Confirm API service status

2. **Email Configuration**
   - Enable less secure app access (if using Gmail)
   - Verify SMTP settings
   - Check firewall settings

3. **Performance Optimization**
   - Adjust batch size settings
   - Configure caching parameters
   - Update Python packages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

Need help? We're here for you!

- 📧 Email: shashikiran05705@gmail.com.com

## 🌟 Acknowledgments

- Thanks to the Groq team for their amazing LLM
- GNews API for providing real-time news access

---
