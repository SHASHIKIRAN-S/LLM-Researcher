"""
Email Configuration Helper
This script helps you set up email configuration for the research assistant.
"""

import os
from dotenv import load_dotenv

def test_email_connection():
    """Test email connection with current settings"""
    import smtplib
    from email.mime.text import MIMEText
    
    load_dotenv()
    
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)
        print("Login successful")
    
    if not email_address or not email_password:
        print("❌ Email credentials not found in .env file")
        return False
    
    try:
        print(f"Testing connection to {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
        
        print("✅ Email configuration is working!")
        return True
        
    except Exception as e:
        print(f"❌ Email configuration error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you're using an App Password (not your regular password)")
        print("2. Enable 2-factor authentication on your email account")
        print("3. Check your SMTP server and port settings")
        return False

def get_smtp_settings():
    """Display common SMTP settings"""
    settings = {
        "Gmail": {
            "server": "smtp.gmail.com",
            "port": "587",
            "notes": "Requires App Password with 2FA enabled"
        },
        "Yahoo": {
            "server": "smtp.mail.yahoo.com",
            "port": "587",
            "notes": "Requires App Password"
        },
        "Outlook/Hotmail": {
            "server": "smtp-mail.outlook.com",
            "port": "587",
            "notes": "May require App Password"
        },
        "iCloud": {
            "server": "smtp.mail.me.com",
            "port": "587",
            "notes": "Requires App-Specific Password"
        }
    }
    
    print("\nCommon SMTP Settings:")
    print("-" * 50)
    for provider, config in settings.items():
        print(f"{provider}:")
        print(f"  Server: {config['server']}")
        print(f"  Port: {config['port']}")
        print(f"  Notes: {config['notes']}")
        print()

def setup_gmail_instructions():
    """Show step-by-step Gmail setup instructions"""
    print("\nGmail Setup Instructions:")
    print("-" * 30)
    print("1. Go to your Google Account settings")
    print("2. Security > 2-Step Verification > Enable it")
    print("3. Security > App passwords")
    print("4. Select app: Mail")
    print("5. Select device: Other (custom name)")
    print("6. Copy the generated 16-character password")
    print("7. Use this password in your .env file (not your regular Gmail password)")
    print("\nExample .env entry:")
    print("EMAIL_ADDRESS=youremail@gmail.com")
    print("EMAIL_PASSWORD=abcd efgh ijkl mnop  # (16-character app password)")

def setup_email_configuration():
    """Interactive email configuration setup"""
    print("\nEmail Configuration Setup")
    print("-" * 30)
    
    # Get current .env content
    env_path = ".env"
    env_content = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_content[key] = value
    
    print("\nSelect your email provider:")
    providers = {
        "1": {"name": "Gmail", "server": "smtp.gmail.com", "port": "587"},
        "2": {"name": "Yahoo", "server": "smtp.mail.yahoo.com", "port": "587"},
        "3": {"name": "Outlook/Hotmail", "server": "smtp-mail.outlook.com", "port": "587"},
        "4": {"name": "iCloud", "server": "smtp.mail.me.com", "port": "587"},
        "5": {"name": "Custom", "server": "", "port": ""}
    }
    
    for key, provider in providers.items():
        print(f"{key}. {provider['name']}")
    
    provider_choice = input("\nSelect provider (1-5): ").strip()
    
    if provider_choice not in providers:
        print("Invalid selection.")
        return
    
    selected_provider = providers[provider_choice]
    
    # Get email settings
    email_address = input(f"\nEnter your {selected_provider['name']} email address: ").strip()
    
    if provider_choice == "5":  # Custom
        smtp_server = input("Enter SMTP server: ").strip()
        smtp_port = input("Enter SMTP port (usually 587): ").strip()
    else:
        smtp_server = selected_provider['server']
        smtp_port = selected_provider['port']
    
    print(f"\nFor {selected_provider['name']}, you need an App Password (not your regular password)")
    email_password = input("Enter your App Password: ").strip()
    
    # Update environment variables
    env_content['EMAIL_ADDRESS'] = email_address
    env_content['EMAIL_PASSWORD'] = email_password
    env_content['SMTP_SERVER'] = smtp_server
    env_content['SMTP_PORT'] = smtp_port
    
    # Write to .env file
    try:
        with open(env_path, 'w') as f:
            f.write("# API Keys\n")
            if 'GROQ_API_KEY' in env_content:
                f.write(f"GROQ_API_KEY={env_content['GROQ_API_KEY']}\n")
            else:
                f.write("GROQ_API_KEY=your_groq_api_key_here\n")
            
            if 'GNEWS_API_KEY' in env_content:
                f.write(f"GNEWS_API_KEY={env_content['GNEWS_API_KEY']}\n")
            else:
                f.write("GNEWS_API_KEY=your_gnews_api_key_here\n")
            
            f.write("\n# Email Configuration\n")
            f.write(f"EMAIL_ADDRESS={email_address}\n")
            f.write(f"EMAIL_PASSWORD={email_password}\n")
            f.write(f"SMTP_SERVER={smtp_server}\n")
            f.write(f"SMTP_PORT={smtp_port}\n")
        
        print(f"\n✅ Email configuration saved to {env_path}")
        
        # Test the configuration
        test_now = input("\nWould you like to test the configuration now? (y/n): ").strip().lower()
        if test_now == 'y':
            # Reload environment variables
            load_dotenv(override=True)
            test_email_connection()
            
    except Exception as e:
        print(f"❌ Error saving configuration: {str(e)}")

def main():
    print("Research Assistant Email Configuration Helper")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Test current email configuration")
        print("2. Show SMTP settings for common providers")
        print("3. Gmail setup instructions")
        print("4. Set up email configuration")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            test_email_connection()
        elif choice == '2':
            get_smtp_settings()
        elif choice == '3':
            setup_gmail_instructions()
        elif choice == '4':
            setup_email_configuration()
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please select 1-5.")

if __name__ == "__main__":
    main()