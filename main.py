from dotenv import load_dotenv
import os
from pydantic import BaseModel
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from typing import List, Optional
import feedparser
from datetime import datetime, timezone
import time

# Load environment variables from .env
load_dotenv()

# Define your output schema with Pydantic
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]
    recent_news: Optional[List[str]] = None

# Initialize Wikipedia tool with better settings
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(
    top_k_results=3,
    load_max_docs=3,
    doc_content_chars_max=2000
))

# Define major news sources RSS feeds with categories
NEWS_SOURCES = {
    # General News
    "Reuters": "https://www.reutersagency.com/feed/",
    "Associated Press": "https://feeds.feedburner.com/apnews/world",
    "NPR": "https://feeds.npr.org/1001/rss.xml",
    "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    
    # Technology
    "TechCrunch": "https://feeds.feedburner.com/TechCrunch",
    "Wired": "https://www.wired.com/feed/rss",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    
    # Science
    "Scientific American": "http://rss.sciam.com/ScientificAmerican-Global",
    "Science Daily": "https://www.sciencedaily.com/rss/all.xml",
    "Nature": "http://feeds.nature.com/nature/rss/current",
    "Space.com": "https://www.space.com/feeds/all",
    
    # Business & Finance
    "Forbes": "https://www.forbes.com/business/feed/",
    "Financial Times": "https://www.ft.com/rss/home",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    
    # Health & Medicine
    "Medical News Today": "https://rss.medicalnewstoday.com/all-news.xml",
    "WHO News": "https://www.who.int/rss-feeds/news-english.xml",
    "CDC": "https://tools.cdc.gov/api/v2/resources/media/403372.rss",
    
    # Environment
    "Environmental News Network": "https://www.enn.com/rss",
    "GreenBiz": "https://www.greenbiz.com/rss.xml",
    "CleanTechnica": "https://cleantechnica.com/feed/"
}

def research_topic(query: str) -> ResearchResponse:
    """Research a topic using Wikipedia and news sources"""
    try:
        # Get Wikipedia summary
        wiki_result = wikipedia.run(query)
        
        # Get recent news
        news_results = []
        try:
            news_results = get_recent_news(query)
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
        
        # Create response
        response = ResearchResponse(
            topic=query,
            summary=wiki_result,
            sources=["Wikipedia"],
            tools_used=["Wikipedia Search"],
            recent_news=news_results
        )
        
        return response
    except Exception as e:
        print(f"Error in research_topic: {str(e)}")
        # Return basic response with error
        return ResearchResponse(
            topic=query,
            summary=f"Error researching topic: {str(e)}",
            sources=[],
            tools_used=[],
            recent_news=[]
        )

def parse_date(date_str: str) -> datetime:
    """Parse various date formats to datetime object"""
    try:
        # Try parsing common RSS date formats
        for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If standard formats fail, use feedparser's date parser
        parsed = feedparser._parse_date(date_str)
        if parsed:
            return datetime(*parsed[:6])
        
        # Last resort: current time
        return datetime.now(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)

def get_recent_news(query: str, max_results: int = 3) -> List[str]:
    """Get recent news articles using RSS feeds from multiple sources"""
    try:
        print("Fetching news from RSS feeds...")
        all_articles = []
        query_terms = set(query.lower().split())
        
        # Track which categories have matched articles
        category_matches = {
            "General News": [],
            "Technology": [],
            "Science": [],
            "Business": [],
            "Health": [],
            "Environment": []
        }
        
        for source, feed_url in NEWS_SOURCES.items():
            try:
                # Parse the RSS feed
                feed = feedparser.parse(feed_url)
                
                # Determine category based on source
                category = "General News"
                if source in ["TechCrunch", "Wired", "The Verge", "Ars Technica"]:
                    category = "Technology"
                elif source in ["Scientific American", "Science Daily", "Nature", "Space.com"]:
                    category = "Science"
                elif source in ["Forbes", "Financial Times", "Bloomberg"]:
                    category = "Business"
                elif source in ["Medical News Today", "WHO News", "CDC"]:
                    category = "Health"
                elif source in ["Environmental News Network", "GreenBiz", "CleanTechnica"]:
                    category = "Environment"
                
                # Process each entry in the feed
                for entry in feed.entries:
                    # Check if article matches query
                    title = entry.get('title', '').lower()
                    description = entry.get('description', '').lower()
                    
                    # Check if any query term is in title or description
                    if any(term in title or term in description for term in query_terms):
                        # Get publication date
                        pub_date = entry.get('published', entry.get('updated', ''))
                        if pub_date:
                            date = parse_date(pub_date)
                            date_str = date.strftime('%Y-%m-%d %H:%M UTC')
                        else:
                            date_str = 'Date unknown'
                        
                        article = {
                            'title': entry.get('title', 'No title'),
                            'date': date_str,
                            'source': source,
                            'category': category,
                            'timestamp': date if pub_date else datetime.now(timezone.utc),
                            'link': entry.get('link', '')
                        }
                        
                        # Add to both overall list and category-specific list
                        all_articles.append(article)
                        category_matches[category].append(article)
                
            except Exception as e:
                print(f"Error fetching from {source}: {str(e)}")
                continue
        
        # Sort articles by date (newest first)
        all_articles.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Try to get articles from different categories if possible
        selected_articles = []
        categories_with_matches = [cat for cat, matches in category_matches.items() if matches]
        
        if categories_with_matches:
            # First, take one article from each category that has matches
            for category in categories_with_matches:
                if len(selected_articles) < max_results:
                    category_matches[category].sort(key=lambda x: x['timestamp'], reverse=True)
                    selected_articles.append(category_matches[category][0])
            
            # If we still need more articles, take the newest remaining ones
            remaining_slots = max_results - len(selected_articles)
            if remaining_slots > 0:
                remaining_articles = [a for a in all_articles if a not in selected_articles]
                selected_articles.extend(remaining_articles[:remaining_slots])
        else:
            # If no category matches, just take the top results
            selected_articles = all_articles[:max_results]
        
        if not selected_articles:
            print("No relevant articles found in RSS feeds")
            # Fallback to DuckDuckGo
            return get_news_from_duckduckgo(query, max_results)
        
        # Format the results with category
        return [f"{article['title']} ({article['category']}: {article['source']}, {article['date']})" 
                for article in selected_articles]
            
    except Exception as e:
        print(f"Error fetching news from RSS feeds: {str(e)}")
        # Fallback to DuckDuckGo
        return get_news_from_duckduckgo(query, max_results)

def get_news_from_duckduckgo(query: str, max_results: int = 3) -> List[str]:
    """Fallback function to get news from DuckDuckGo"""
    try:
        from duckduckgo_search import DDGS
        
        print("Falling back to DuckDuckGo News...")
        with DDGS() as ddgs:
            news_results = list(ddgs.news(
                keywords=query,
                region="wt-wt",
                safesearch="moderate",
                timelimit="w",  # Get news from the last week
                max_results=max_results
            ))
            
            if not news_results:
                print("No articles found in DuckDuckGo")
                return []
                
            return [f"{article['title']} ({article['date']})" for article in news_results]
            
    except Exception as e:
        print(f"Error fetching news from DuckDuckGo: {str(e)}")
        return []

def print_results(result: ResearchResponse):
    """Print research results in a user-friendly, formatted way"""
    print("\n" + "="*80)
    print(f"📚 Research Results: {result.topic}")
    print("="*80 + "\n")
    
    # Print the summary with better formatting
    print("📋 Summary:")
    print("-"*80)
    # Split summary into paragraphs and add proper spacing
    paragraphs = result.summary.split('\n')
    for paragraph in paragraphs:
        if paragraph.strip():
            print(f"{paragraph}\n")
    
    # Print news results with categories and suggestions
    if result.recent_news:
        print("\n📰 Recent News by Category:")
        print("-"*80)
        
        # Group news by category
        news_by_category = {}
        for news in result.recent_news:
            # Extract category from the news string
            category = news[news.find("(")+1:news.find(":")]
            if category not in news_by_category:
                news_by_category[category] = []
            news_by_category[category].append(news)
        
        # Print news by category with emoji indicators
        category_emojis = {
            "Technology": "💻",
            "Science": "🔬",
            "Business": "💼",
            "Health": "🏥",
            "Environment": "🌍",
            "General News": "📢"
        }
        
        for category, news_items in news_by_category.items():
            emoji = category_emojis.get(category, "•")
            print(f"\n{emoji} {category}:")
            for news in news_items:
                # Clean up the news string format
                title = news[:news.find("(")].strip()
                metadata = news[news.find("(")+1:news.find(")")].strip()
                print(f"  • {title}")
                print(f"    [{metadata}]\n")
        
        # Add relevant suggestions based on categories found
        print("\n💡 Suggested Related Topics:")
        print("-"*80)
        suggestions = set()  # Use set to avoid duplicates
        
        category_suggestions = {
            "Technology": ["AI developments", "cybersecurity", "tech innovations"],
            "Science": ["research breakthroughs", "scientific discoveries", "space exploration"],
            "Business": ["market trends", "industry analysis", "economic impact"],
            "Health": ["medical research", "healthcare innovations", "public health"],
            "Environment": ["climate initiatives", "sustainability", "renewable energy"],
            "General News": ["global impact", "policy changes", "international relations"]
        }
        
        for category in news_by_category.keys():
            if category in category_suggestions:
                suggestions.update(category_suggestions[category])
        
        # Print 3-5 relevant suggestions
        suggestions = list(suggestions)[:5]
        for suggestion in suggestions:
            print(f"  • Try researching: '{result.topic} and {suggestion}'")
    
    # Print sources with emoji indicators
    print("\n📚 Sources Used:")
    print("-"*80)
    for source in result.sources:
        print(f"  • {source}")
    
    # Print research tips
    print("\n💭 Research Tips:")
    print("-"*80)
    print("  • Try using more specific keywords for focused results")
    print("  • Combine topics from different categories for comprehensive research")
    print("  • Use quotation marks for exact phrase matching")
    
    print("\n" + "="*80)
    print("Want to explore more? Try a new search or type 'exit' to quit.")
    print("="*80 + "\n")

def format_results_for_email(result: ResearchResponse) -> tuple[str, str]:
    """Format research results for email in a clean, readable format"""
    subject = f"Research Results: {result.topic}"
    
    body = f"""
{'='*50}
📚 Research Results: {result.topic}
{'='*50}

📋 Summary:
{'-'*50}
{result.summary}

"""
    if result.recent_news:
        body += "\n📰 Recent News by Category:\n"
        body += f"{'-'*50}\n"
        
        # Group news by category
        news_by_category = {}
        for news in result.recent_news:
            category = news[news.find("(")+1:news.find(":")]
            if category not in news_by_category:
                news_by_category[category] = []
            news_by_category[category].append(news)
        
        # Add news by category
        category_emojis = {
            "Technology": "💻",
            "Science": "🔬",
            "Business": "💼",
            "Health": "🏥",
            "Environment": "🌍",
            "General News": "📢"
        }
        
        for category, news_items in news_by_category.items():
            emoji = category_emojis.get(category, "•")
            body += f"\n{emoji} {category}:\n"
            for news in news_items:
                title = news[:news.find("(")].strip()
                metadata = news[news.find("(")+1:news.find(")")].strip()
                body += f"  • {title}\n"
                body += f"    [{metadata}]\n"
    
    body += f"\n📚 Sources Used:\n{'-'*50}\n"
    for source in result.sources:
        body += f"  • {source}\n"
    
    body += f"\n💭 Research Tips:\n{'-'*50}\n"
    body += "  • Try using more specific keywords for focused results\n"
    body += "  • Combine topics from different categories for comprehensive research\n"
    body += "  • Use quotation marks for exact phrase matching\n"
    
    body += f"\n{'='*50}\n"
    
    return subject, body

def main():
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
