import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import socket

# Keep the IPv4 patch just in case, it helps with connectivity
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4_only

def send_email(to_email, subject, body):
    # Load variables from Environment
    smtp_server = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    smtp_port = int(os.environ.get('MAIL_PORT') or 587)
    sender_email = os.environ.get('MAIL_USERNAME') # For SendGrid, this is usually "apikey"
    sender_password = os.environ.get('MAIL_PASSWORD') # This will be the API Key
    sender_from = os.environ.get('MAIL_DEFAULT_SENDER') # The email address users see

    print(f"📧 Sending to {to_email} via {smtp_server}...")

    if not sender_email or not sender_password:
        print("❌ Error: Missing credentials.")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_from
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Use standard TLS connection (Best for SendGrid)
        with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as server:
            server.set_debuglevel(1)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_from, to_email, msg.as_string())
        
        print(f"✅ Email sent successfully!")
        return True

    except Exception as e:
        print(f"❌ EMAIL FAILED: {e}")
        raise 

# Wrappers
def send_reminder_email(to_email, task_title, due_date):
    send_email(to_email, f"Reminder: {task_title}", f"Your task '{task_title}' is due at {due_date}.")

def send_reset_code(to_email, code):
    send_email(to_email, "Reset Code", f"Your code is: {code}")