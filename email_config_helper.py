"""
Email Configuration Helper
This script helps you set up email configuration for the research assistant.
"""

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

def test_email_connection():
    """Test email connection with current settings"""
    load_dotenv()
    
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        print("❌ Email configuration not found in .env file")
        return False
    
    try:
        print(f"Testing connection to {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            print("✅ Email configuration is working!")
            return True
            
    except Exception as e:
        print(f"❌ Email configuration error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you're using an App Password (not your regular password)")
        print("2. Enable 2-factor authentication on your email account")
        print("3. Check your SMTP server and port settings")
        return False

def setup_email_config():
    """Interactive setup for email configuration"""
    print("\nEmail Configuration Setup")
    print("-" * 30)
    
    # Get provider details
    print("\nSelect your email provider:")
    providers = {
        "1": {"name": "Gmail", "server": "smtp.gmail.com", "port": "587"},
        "2": {"name": "Outlook", "server": "smtp-mail.outlook.com", "port": "587"},
        "3": {"name": "Yahoo", "server": "smtp.mail.yahoo.com", "port": "587"},
        "4": {"name": "Custom", "server": "", "port": ""}
    }
    
    for key, provider in providers.items():
        print(f"{key}. {provider['name']}")
    
    choice = input("\nSelect provider (1-4): ").strip()
    if choice not in providers:
        print("Invalid selection.")
        return
    
    provider = providers[choice]
    
    # Get email settings
    sender_email = input(f"\nEnter your {provider['name']} email address: ").strip()
    
    if choice == "4":  # Custom provider
        smtp_server = input("Enter SMTP server: ").strip()
        smtp_port = input("Enter SMTP port: ").strip()
    else:
        smtp_server = provider["server"]
        smtp_port = provider["port"]
    
    print("\nFor security, use an App Password instead of your regular password.")
    print("To generate an App Password:")
    print("1. Enable 2-factor authentication on your account")
    print("2. Go to your account's security settings")
    print("3. Generate an App Password for this application")
    sender_password = input("\nEnter your App Password: ").strip()
    
    # Create or update .env file
    env_content = f"""# Email Configuration
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
SENDER_EMAIL={sender_email}
SENDER_PASSWORD={sender_password}
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("\n✅ Email configuration saved to .env file")
        
        # Test the configuration
        if input("\nWould you like to test the configuration? (y/n): ").lower() == 'y':
            test_email_connection()
            
    except Exception as e:
        print(f"❌ Error saving configuration: {str(e)}")

if __name__ == "__main__":
    print("Research Assistant Email Configuration Helper")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Set up email configuration")
        print("2. Test current configuration")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            setup_email_config()
        elif choice == '2':
            test_email_connection()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1-3.")