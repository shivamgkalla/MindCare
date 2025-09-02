import smtplib
from email.mime.text import MIMEText
from src.core.config import settings



def send_email(to_email: str, subject: str, body: str):

    if settings.DEV_MODE:
        # Print email to console for dev/testing
        print(f"\n--- Email (DEV_MODE) ---\nTo: {to_email}\nSubject: {subject}\n{body}\n-----------------------\n")
    
    else:
        # Send real email via SMTP
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)
        except Exception as e:
            print("Error sending email:", e)
            raise e