from dotenv import load_dotenv
import os
from langchain_anthropic import ChatAnthropic

def test_anthropic_api():
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file")
        return False
        
    try:
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
        response = llm.invoke("Say 'API is working!'")
        print("✅ API key is valid! Test response:", response)
        return True
    except Exception as e:
        print("❌ Error testing API key:", str(e))
        return False

if __name__ == "__main__":
    test_anthropic_api() 