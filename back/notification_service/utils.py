import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from back.config import NotificationSettings

notification_settings = NotificationSettings()


async def send_email(email: str, subject: str, body: str):
    message = MIMEMultipart()
    message["From"] = notification_settings.SMTP_USER
    message["To"] = email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(notification_settings.SMTP_HOST, notification_settings.SMTP_PORT) as server:
        server.login(notification_settings.SMTP_USER, notification_settings.SMTP_PASSWORD)
        server.send_message(message)
