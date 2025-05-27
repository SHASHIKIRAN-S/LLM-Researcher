from dotenv import load_dotenv
import os
from pydantic import BaseModel
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_groq import ChatGroq
import json
import requests
from typing import List, Optional
from email_sender import send_email

# Load environment variables from .env
load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
PORT = int(os.getenv("SMTP_PORT", 587))
# Get API keys from environment
groq_api_key = os.getenv("GROQ_API_KEY")
gnews_api_key = os.getenv("GNEWS_API_KEY")
print(f"Groq API Key loaded: {groq_api_key is not None}")
print(f"GNews API Key loaded: {gnews_api_key is not None}")

# Define your output schema with Pydantic
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]
    recent_news: Optional[List[str]] = None

# Initialize Groq LLM client
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    groq_api_key=groq_api_key,
    temperature=0,
    max_tokens=2000,
)

# Initialize Wikipedia tool with better settings
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(
    top_k_results=3,
    load_max_docs=3,
    doc_content_chars_max=2000
))

def get_recent_news(query: str, max_results: int = 3) -> List[str]:
    """Get recent news articles from GNews API"""
    if not gnews_api_key:
        print("GNews API key not found")
        return []
        
    try:
        print("Fetching news from GNews API...")
        # Format query for GNews API
        formatted_query = query.replace(" ", "+").strip("?!.,")
        url = f"https://gnews.io/api/v4/search?q={formatted_query}&lang=en&country=us&max={max_results}&apikey={gnews_api_key}"
        response = requests.get(url)
        print(f"GNews API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            if not articles:
                print("No articles found in the response")
            return [f"{article['title']} ({article['publishedAt']})" for article in articles]
        else:
            print(f"Error response from GNews API: {response.text}")
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
    return []

def research_topic(query: str) -> ResearchResponse:
    try:
        # First, get information from Wikipedia
        wiki_result = wikipedia.run(query)
        
        # Get recent news
        news_results = get_recent_news(query)
        
        # Combine information for the LLM
        context = f"""Information from Wikipedia:
{wiki_result}

Recent News Articles:
{chr(10).join(['- ' + news for news in news_results]) if news_results else 'No recent news available.'}
"""
        
        # Use the LLM to summarize and format the information
        prompt = f"""Based on the following information about {query}, please provide a clear and concise summary:

{context}

Please focus on the most relevant and recent information in your summary."""

        summary = llm.invoke(prompt)
        
        # Determine sources and tools used
        sources = ["Wikipedia"]
        tools_used = ["wikipedia"]
        if news_results:
            sources.append("GNews")
            tools_used.append("gnews")
        
        return ResearchResponse(
            topic=query,
            summary=summary.content if hasattr(summary, 'content') else str(summary),
            sources=sources,
            tools_used=tools_used,
            recent_news=news_results if news_results else None
        )
        
    except Exception as e:
        print(f"Error during research: {e}")
        return ResearchResponse(
            topic=query,
            summary="Error processing the request",
            sources=[],
            tools_used=[],
            recent_news=None
        )

def print_results(result: ResearchResponse):
    """Print research results in a formatted way"""
    print("\nResearch Results:")
    print(f"Topic: {result.topic}")
    print(f"\nSummary:")
    print(result.summary)
    
    if result.recent_news:
        print(f"\nRecent News:")
        for news in result.recent_news:
            print(f"- {news}")
    
    print(f"\nSources: {', '.join(result.sources)}")
    print(f"Tools Used: {', '.join(result.tools_used)}")

def format_results_for_email(result: ResearchResponse) -> tuple[str, str]:
    """Format research results for email"""
    subject = f"Research Results: {result.topic}"
    
    body = f"""Research Results for: {result.topic}

Summary:
{result.summary}

"""
    if result.recent_news:
        body += "\nRecent News:\n"
        for news in result.recent_news:
            body += f"- {news}\n"
    
    body += f"\nSources: {', '.join(result.sources)}"
    body += f"\nTools Used: {', '.join(result.tools_used)}"
    
    return subject, body

def main():
    # Check if GNews API key is missing
    if not gnews_api_key:
        print("\nNote: GNews API key not found. Only Wikipedia results will be available.")
        print("To enable real-time news, create a free account at https://gnews.io/")
        print("Then add your API key to the .env file as GNEWS_API_KEY=your_key_here\n")
    
    while True:
        try:
            query = input("\nWhat can I help you research? (type 'exit' to quit) ")
            
            # Check for exit command
            if query.lower() in ['exit', 'quit', 'q']:
                print("\nThank you for using the research assistant. Goodbye!")
                break
                
            # Skip empty queries
            if not query.strip():
                print("Please enter a valid query.")
                continue
            
            result = research_topic(query)
            print_results(result)
            
            # Ask if user wants to email the results
            send_to_email = input("\nWould you like to receive these results via email? (y/n): ").strip().lower()
            if send_to_email == 'y':
                recipient = input("Enter your email address: ").strip()
                subject, body = format_results_for_email(result)
                try:
                    send_email(recipient, subject, body)
                except Exception as e:
                    print(f"Failed to send email: {str(e)}")
            
            print("\n" + "-"*50)  # Add a separator line
            
        except Exception as e:
            print(f"Error: {e}")
            print("An error occurred. Let's try another search.")
            continue
        except KeyboardInterrupt:
            print("\n\nThank you for using the research assistant. Goodbye!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user. Goodbye!")
