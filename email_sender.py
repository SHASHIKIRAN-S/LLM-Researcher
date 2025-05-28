"""
Email Sender Module
Handles sending emails using SMTP with environment-based configuration.
"""

import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def send_email(recipient, subject, body):
    """
    Send an email using configured SMTP settings from environment variables.
    
    Args:
        recipient (str): Email address of the recipient
        subject (str): Subject line of the email
        body (str): Content of the email
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Get credentials from environment variables
    sender = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("SENDER_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    if not all([sender, app_password, smtp_server, smtp_port]):
        error_msg = "Missing email configuration. Please check your .env file."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    try:
        # Create email message
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, 'plain'))
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        
        logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        
        # Connect to SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            
            logger.info("Attempting to log in...")
            smtp.login(sender, app_password)
            
            logger.info("Sending email...")
            smtp.send_message(msg)
            
            logger.info("✅ Email sent successfully!")
            return True
            
    except smtplib.SMTPAuthenticationError as e:
        logger.error("Authentication failed. Please check your email and app password.")
        logger.error(str(e))
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

def validate_email_config() -> bool:
    """
    Check if email configuration is properly set up
    
    Returns:
        bool: True if all required environment variables are set
    """
    required_vars = ["SMTP_SERVER", "SMTP_PORT", "SENDER_EMAIL", "SENDER_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Missing email configuration variables: {', '.join(missing_vars)}")
        return False
    return True

if __name__ == "__main__":
    # Example usage
    try:
        if not validate_email_config():
            print("Please configure email settings in .env file first.")
            exit(1)
            
        recipient = input("Enter recipient email: ").strip()
        subject = input("Enter email subject: ").strip()
        body = input("Enter email body: ").strip()
        
        if send_email(recipient, subject, body):
            print("Email sent successfully!")
        else:
            print("Failed to send email. Check the logs for details.")
    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except Exception as e:
        print(f"Error: {str(e)}") 