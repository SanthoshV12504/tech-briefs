import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "santhoshvelmurugan009@gmail.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "aalo ilzz ykgo qcvf")

def send_email_with_pdf(recipient_email, pdf_path):
    if not os.path.exists(pdf_path):
        return False, f"File not found: {pdf_path}"

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f"TechBriefs Daily: {os.path.basename(pdf_path)}"

        body = "Hello! Here is your daily TechBriefs PDF. Stay updated with the latest in technology."
        msg.attach(MIMEText(body, 'plain'))

        with open(pdf_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(pdf_path)}",
            )
            msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True, "Email sent successfully!"
    except Exception as e:
        return False, str(e)
