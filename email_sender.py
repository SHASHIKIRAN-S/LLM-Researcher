"""
Email Sender Module
Handles sending emails using SMTP with environment-based configuration.
"""

import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

# Load environment variables
load_dotenv()

def send_email(recipient, subject, body):
    """
    Send an email using configured SMTP settings from environment variables.
    
    Args:
        recipient (str): Email address of the recipient
        subject (str): Subject line of the email
        body (str): Content of the email
    """
    # Get credentials from environment variables
    sender = os.getenv("EMAIL_ADDRESS")
    app_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    if not all([sender, app_password, smtp_server, smtp_port]):
        raise ValueError("Missing email configuration. Please run email_config_helper.py first.")
    
    # Create email message
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    
    try:
        # Connect to SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(sender, app_password)
            smtp.send_message(msg)
        print("✅ Email sent successfully!")
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    try:
        recipient = input("Enter recipient email: ").strip()
        subject = input("Enter email subject: ").strip()
        body = input("Enter email body: ").strip()
        
        send_email(recipient, subject, body)
    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except Exception as e:
        print(f"Error: {str(e)}") 