# test_sendgrid.py
import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent

load_dotenv()

API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")

print(f"API Key exists: {'YES' if API_KEY else 'NO'}")
print(f"API Key length: {len(API_KEY) if API_KEY else 0}")
print(f"From Email: {FROM_EMAIL}")

if API_KEY:
    try:
        # Test connection
        sg = SendGridAPIClient(API_KEY)
        print("✅ SendGrid client created successfully")
        
        # Test email
        message = Mail(
            from_email=From(FROM_EMAIL, "HEWAL3 Test"),
            to_emails=To("anane365221@gmail.com"),  # Send to yourself
            subject=Subject("HEWAL3 SendGrid Test"),
            html_content=HtmlContent("<h1>Test Email</h1><p>If you receive this, SendGrid works!</p>")
        )
        
        response = sg.send(message)
        print(f"✅ Test email sent! Status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("❌ No API key found in .env")