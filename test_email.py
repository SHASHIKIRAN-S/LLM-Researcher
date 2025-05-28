"""
Test Email Configuration and Sending
"""
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_config():
    # Load environment variables
    load_dotenv()
    
    # Get email configuration
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    print("\nEmail Configuration:")
    print(f"SMTP Server: {smtp_server}")
    print(f"SMTP Port: {smtp_port}")
    print(f"Sender Email: {sender_email}")
    print(f"Password configured: {'Yes' if sender_password else 'No'}\n")
    
    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        print("❌ Error: Missing email configuration!")
        print("Please make sure your .env file contains:")
        print("SMTP_SERVER=smtp.gmail.com")
        print("SMTP_PORT=587")
        print("SENDER_EMAIL=your.gmail.address@gmail.com")
        print("SENDER_PASSWORD=your-app-specific-password")
        return False
    
    try:
        print(f"Attempting to connect to {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.ehlo()
            print("✓ SMTP connection successful")
            
            print("Starting TLS encryption...")
            server.starttls()
            print("✓ TLS encryption enabled")
            
            print("Attempting login...")
            server.login(sender_email, sender_password)
            print("✓ Login successful!")
            
            # Try sending a test email
            print("\nSending test email...")
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = sender_email  # Send to self
            msg['Subject'] = 'Test Email'
            msg.attach(MIMEText('This is a test email to verify the configuration.', 'plain'))
            
            server.send_message(msg)
            print("✓ Test email sent successfully!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if "Authentication" in str(e):
            print("\nTroubleshooting tips for Gmail:")
            print("1. Make sure you've enabled 2-Step Verification")
            print("2. Generate an App Password:")
            print("   - Go to Google Account settings")
            print("   - Search for 'App Passwords'")
            print("   - Generate a new app password for 'Mail'")
            print("3. Use the generated App Password in your .env file")
        return False

if __name__ == "__main__":
    print("Testing Email Configuration...")
    test_email_config() 