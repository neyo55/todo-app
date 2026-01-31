import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to_email, subject, body):
    sender_email = os.environ.get('MAIL_USERNAME')
    sender_password = os.environ.get('MAIL_PASSWORD')
    
    if not sender_email or not sender_password:
        print("❌ Error: Missing email credentials in environment variables.")
        return False

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # === FIX: Use SMTP_SSL on Port 465 (Prevents Timeouts) ===
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        # Raise the error so the Debug Route sees it
        raise e 

# Wrapper for Task Reminders
def send_reminder_email(to_email, task_title, due_date):
    subject = f"Reminder: {task_title} is due!"
    body = f"Hello,\n\nYour task '{task_title}' is due at {due_date}.\n\nGet it done!\n- ProTodo"
    send_email(to_email, subject, body)

# Wrapper for Password Reset
def send_reset_code(to_email, code):
    subject = "Password Reset Code"
    body = f"Your ProTodo reset code is: {code}\n\nIt expires in 15 minutes."
    send_email(to_email, subject, body)