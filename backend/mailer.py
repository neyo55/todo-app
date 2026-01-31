# mailer.py - Send reminder emails using Gmail SMTP (development only)

# backend/mailer.py
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body):
    sender_email = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def send_reminder_email(to_email, task_title, due_time):
    subject = f"🔔 Reminder: {task_title}"
    body = f"""
    <h2>ProTodo Reminder</h2>
    <p>Hey there! Just a heads up about your task:</p>
    <p><strong>Task:</strong> {task_title}</p>
    <p><strong>Due:</strong> {due_time}</p>
    <p>Time to get it done! 🚀</p>
    """
    send_email(to_email, subject, body)

def send_reset_code(to_email, code):
    subject = "🔑 ProTodo Password Reset Code"
    body = f"""
    <h2>Password Reset Request</h2>
    <p>You requested to reset your password. Use the code below:</p>
    <h1 style="color: #4F46E5; font-size: 32px; letter-spacing: 5px;">{code}</h1>
    <p>This code expires in 15 minutes.</p>
    <p>If you didn't request this, please ignore this email.</p>
    """
    send_email(to_email, subject, body)