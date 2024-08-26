import markdown
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import dotenv
import os

dotenv.load_dotenv()

import imaplib
from email.header import decode_header
import dotenv
import os

dotenv.load_dotenv()


class EmailClient:
    def __init__(self):
        self.username = os.getenv('EMAIL_ADDRESS')
        self.app_password = os.getenv('EMAIL_APP_PASSWORD')

        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")  # connect to gmail IMAP server

        self.mail.login(self.username, self.app_password)
        self.mail.select("inbox")

    def send_email(self, subject, body, recipients, is_html=False):

        if isinstance(recipients, str):
            recipients = [recipients]

        # email content
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject

        # attach the body, use 'html' if sending HTML content
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        # start SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        server.login(self.username, self.app_password)

        # convert message to string and send it
        text = msg.as_string()
        server.sendmail(self.username, recipients, text)
        server.quit()
