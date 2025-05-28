import streamlit as st
from dotenv import load_dotenv
import os
from main import research_topic, ResearchResponse, format_results_for_email
from email_sender import send_email, validate_email_config
from typing import Dict, List
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import time
import logging

# Configure logging to show in Streamlit
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables at startup
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Research Assistant",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stAlert {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
    }
    .research-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'research_result' not in st.session_state:
    st.session_state.research_result = None
if 'email_debug' not in st.session_state:
    st.session_state.email_debug = {}

def get_category_color(category: str) -> str:
    """Get color for category badge"""
    colors = {
        "Technology": "#007bff",
        "Science": "#28a745",
        "Business": "#ffc107",
        "Health": "#dc3545",
        "Environment": "#20c997",
        "General News": "#6c757d"
    }
    return colors.get(category, "#6c757d")

def render_news_item(title: str, metadata: str):
    """Render a news item with styling"""
    category = metadata.split(":")[0].strip()
    source_date = metadata.split(":", 1)[1].strip()
    color = get_category_color(category)
    
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <div style="background-color: {color}20; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {color};">
            <div style="color: {color}; font-weight: bold; font-size: 0.875rem; margin-bottom: 0.5rem;">
                {category}
            </div>
            <div style="font-weight: bold; margin-bottom: 0.25rem;">
                {title}
            </div>
            <div style="font-size: 0.875rem; color: #666;">
                {source_date}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def analyze_results(result: ResearchResponse) -> Dict:
    """Analyze research results for visualization"""
    try:
        categories = {}
        if result.recent_news:
            for news in result.recent_news:
                category = news[news.find("(")+1:news.find(":")].strip()
                categories[category] = categories.get(category, 0) + 1
        return categories
    except Exception as e:
        st.error(f"Error analyzing results: {str(e)}")
        return {}

def create_visualizations(categories: Dict):
    """Create visualizations from categories data"""
    try:
        if categories:
            # Extract categories and counts
            cats = list(categories.keys())
            counts = list(categories.values())
            
            # Create visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    # Pie chart using plotly.graph_objects
                    fig1 = go.Figure(data=[go.Pie(
                        labels=cats,
                        values=counts,
                        hole=0.3
                    )])
                    fig1.update_layout(
                        title='News Distribution by Category',
                        showlegend=True
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating pie chart: {str(e)}")
                    st.write("Data:", categories)
            
            with col2:
                try:
                    # Bar chart using plotly.graph_objects
                    fig2 = go.Figure(data=[go.Bar(
                        x=cats,
                        y=counts,
                        marker_color='rgb(55, 83, 109)'
                    )])
                    fig2.update_layout(
                        title='Number of Articles per Category',
                        xaxis_title='Category',
                        yaxis_title='Count',
                        showlegend=False
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating bar chart: {str(e)}")
                    st.write("Data:", categories)
            
            # Add statistics
            st.markdown("### 📈 Quick Stats")
            stats_cols = st.columns(3)
            with stats_cols[0]:
                st.metric("Total Articles", sum(counts))
            with stats_cols[1]:
                st.metric("Categories Found", len(cats))
            with stats_cols[2]:
                most_common_idx = counts.index(max(counts))
                st.metric("Most Common Category", cats[most_common_idx])
            
            # Add debug information
            with st.expander("🔍 Debug Information"):
                st.write("Raw Data:")
                for cat, count in zip(cats, counts):
                    st.write(f"- {cat}: {count}")
        else:
            st.info("No data available for visualization.")
    except Exception as e:
        st.error(f"Error creating visualizations: {str(e)}")
        st.write("Categories data:", categories)

def send_research_email(recipient: str, result: ResearchResponse) -> bool:
    """Helper function to send research results via email with detailed feedback"""
    try:
        # Store debug information
        st.session_state.email_debug = {
            'sender': os.getenv('SENDER_EMAIL'),
            'smtp_server': os.getenv('SMTP_SERVER'),
            'smtp_port': os.getenv('SMTP_PORT'),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Format email content
        subject, body = format_results_for_email(result)
        
        # Send email with logging
        logger.info(f"Attempting to send email to {recipient}")
        success = send_email(recipient, subject, body)
        
        if success:
            st.session_state.email_debug['status'] = 'success'
            logger.info("Email sent successfully")
        else:
            st.session_state.email_debug['status'] = 'failed'
            logger.error("Failed to send email")
            
        return success
    except Exception as e:
        st.session_state.email_debug['status'] = 'error'
        st.session_state.email_debug['error'] = str(e)
        logger.error(f"Error sending email: {str(e)}")
        return False

def main():
    # Sidebar
    with st.sidebar:
        st.title("📚 Research Assistant")
        st.markdown("---")
        
        # Search History
        if st.session_state.search_history:
            st.subheader("Recent Searches")
            for topic in reversed(st.session_state.search_history[-5:]):
                if st.button(f"🔄 {topic}", key=f"history_{topic}"):
                    st.session_state.query = topic
            st.markdown("---")
        
        # Email Configuration Status
        email_configured = validate_email_config()
        if email_configured:
            st.success("✉️ Email functionality is configured")
            st.info(f"Sender Email: {os.getenv('SENDER_EMAIL')}")
            st.info(f"SMTP Server: {os.getenv('SMTP_SERVER')}:{os.getenv('SMTP_PORT')}")
        else:
            st.warning("""
            ⚠️ Email functionality is not configured.
            To enable email:
            1. Create a .env file
            2. Add the following variables:
               - SMTP_SERVER (e.g., smtp.gmail.com)
               - SMTP_PORT (e.g., 587)
               - SENDER_EMAIL
               - SENDER_PASSWORD
            """)
        
        st.markdown("---")
        
        # About section
        st.markdown("""
        ### About
        This app helps you research topics by combining information from Wikipedia and recent news sources.
        Enter a topic below to get started!
        
        ### Sources
        Information is gathered from:
        - Wikipedia
        - RSS News Feeds
        - Multiple Categories
        """)
    
    # Main content
    st.title("AI Research Assistant")
    st.markdown("Get comprehensive research results from multiple sources")
    
    # Check for API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.warning("""
        ⚠️ Groq API key not found. Only Wikipedia results will be available.
        To enable real-time news:
        1. Create a free account at https://groq.com/
        2. Add your API key to the .env file as GROQ_API_KEY=your_key_here
        """)
    
    # Search input
    query = st.text_input("What would you like to research?", 
                         key="query",
                         placeholder="Enter your research topic...")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 Search", use_container_width=True)
    with col2:
        if st.session_state.search_history:
            clear_history = st.button("🗑️ Clear History", use_container_width=True)
            if clear_history:
                st.session_state.search_history = []
                st.rerun()
    
    if search_button and query:
        # Add to search history
        if query not in st.session_state.search_history:
            st.session_state.search_history.append(query)
        
        # Show progress
        with st.status("Researching...") as status:
            st.write("🔍 Searching multiple sources...")
            try:
                result = research_topic(query)
                st.session_state.research_result = result  # Store result in session state
                st.write("📊 Analyzing results...")
                time.sleep(1)
                status.update(label="Research complete!", state="complete")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                status.update(label="Research failed!", state="error")
                return
        
        # Display results in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "📰 News", "📊 Analysis", "✉️ Email"])
        
        with tab1:
            st.markdown("### Research Summary")
            st.markdown(result.summary)
            
            st.markdown("### Sources Used")
            for source in result.sources:
                st.markdown(f"- {source}")
        
        with tab2:
            if result.recent_news:
                # Group news by category
                news_by_category = {}
                for news in result.recent_news:
                    category = news[news.find("(")+1:news.find(":")].strip()
                    if category not in news_by_category:
                        news_by_category[category] = []
                    news_by_category[category].append(news)
                
                # Display news by category
                for category, news_items in news_by_category.items():
                    st.markdown(f"### {category}")
                    for news in news_items:
                        title = news[:news.find("(")].strip()
                        metadata = news[news.find("(")+1:news.find(")")].strip()
                        st.markdown(f"""
                        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem;'>
                            <div style='font-weight: bold;'>{title}</div>
                            <div style='color: #666; font-size: 0.875rem;'>{metadata}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No recent news found for this topic.")
        
        with tab3:
            st.markdown("### 📊 Analysis Dashboard")
            categories = analyze_results(result)
            create_visualizations(categories)
            
            # Suggestions section
            st.markdown("### 💡 Suggested Related Topics")
            suggestions = []
            for category in categories.keys():
                if category == "Technology":
                    suggestions.extend(["AI developments", "cybersecurity", "tech innovations"])
                elif category == "Science":
                    suggestions.extend(["research breakthroughs", "scientific discoveries"])
                elif category == "Business":
                    suggestions.extend(["market trends", "economic impact"])
                elif category == "Health":
                    suggestions.extend(["medical research", "healthcare innovations"])
                elif category == "Environment":
                    suggestions.extend(["climate initiatives", "sustainability"])
            
            if suggestions:
                suggestion_cols = st.columns(3)
                for i, suggestion in enumerate(suggestions[:6]):
                    with suggestion_cols[i % 3]:
                        if st.button(f"🔍 {query} and {suggestion}", key=f"sug_{suggestion}"):
                            st.session_state.query = f"{query} and {suggestion}"
                            st.rerun()
        
        with tab4:
            st.markdown("### ✉️ Email Results")
            
            # Show email configuration status with detailed information
            email_config = {
                'SMTP Server': os.getenv('SMTP_SERVER'),
                'SMTP Port': os.getenv('SMTP_PORT'),
                'Sender Email': os.getenv('SENDER_EMAIL'),
                'Password Configured': 'Yes' if os.getenv('SENDER_PASSWORD') else 'No'
            }
            
            with st.expander("📧 Email Configuration", expanded=True):
                for key, value in email_config.items():
                    st.text(f"{key}: {value}")
            
            if validate_email_config():
                # Check if we have research results
                if st.session_state.research_result is None:
                    st.warning("⚠️ Please perform a search first to get results to email.")
                else:
                    recipient = st.text_input("Enter recipient email address:", placeholder="example@email.com")
                    
                    # Show email preview
                    if recipient:
                        with st.expander("📧 Preview Email", expanded=True):
                            subject, body = format_results_for_email(st.session_state.research_result)
                            st.text("Subject: " + subject)
                            st.markdown("---")
                            st.text("Body:")
                            st.text(body)
                    
                    # Send email button with feedback
                    if st.button("📧 Send Results", use_container_width=True) and recipient:
                        with st.spinner("Sending email..."):
                            if send_research_email(recipient, st.session_state.research_result):
                                st.success("✅ Email sent successfully!")
                                st.balloons()
                            else:
                                st.error("❌ Failed to send email.")
                                with st.expander("📧 Debug Information", expanded=True):
                                    st.json(st.session_state.email_debug)
                                st.warning("""
                                If using Gmail:
                                1. Make sure 2-Step Verification is enabled
                                2. Use an App Password instead of your regular password
                                3. Check the email configuration in your .env file
                                """)
            else:
                st.error("""
                ⚠️ Email configuration is incomplete. Please check your .env file and add:
                ```
                SMTP_SERVER=smtp.gmail.com
                SMTP_PORT=587
                SENDER_EMAIL=your.email@gmail.com
                SENDER_PASSWORD=your-app-specific-password
                ```
                For Gmail users:
                1. Enable 2-Step Verification in your Google Account
                2. Generate an App Password:
                   - Go to Google Account settings
                   - Search for 'App Passwords'
                   - Select 'Mail' and your device
                   - Use the generated password in your .env file
                """)

if __name__ == "__main__":
    main() 