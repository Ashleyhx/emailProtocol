import os

from flask import Flask, render_template
import imaplib
import email
from email.header import decode_header

app = Flask(__name__)

username = os.getenv('GMAIL_USERNAME')
password = os.getenv('GMAIL_PASSWORD')


@app.route('/')
def index():
    return render_template("index.html")


def fetch_emails():
    imap_url = 'imap.gmail.com'

    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(username, password)
    mail.select('inbox')

    # Get total number of emails
    res, messages = mail.select('inbox')
    messages = int(messages[0])

    # Specify the number of emails to fetch
    n = 3
    email_data = []

    # Fetch n most recent emails
    for i in range(messages, messages - n, -1):
        res, msg = mail.fetch(str(i), '(RFC822)')
        for response in msg:
            if isinstance(response, tuple):
                # Parse the bytes email into a message object
                msg = email.message_from_bytes(response[1])

                # Decode email sender
                From = decode_header(msg['From'])[0][0]
                if isinstance(From, bytes):
                    From = From.decode()

                # Decode email subject
                subject = decode_header(msg['Subject'])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

                # Assume there might be multiple parts
                body = ''
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == 'text/plain' and 'attachment' not in content_disposition:
                            body = part.get_payload(decode=True).decode()  # decode
                            break
                else:  # extract text/plain emails
                    body = msg.get_payload(decode=True).decode()

                email_data.append({'from': From, 'subject': subject, 'body': body})

    mail.logout()
    return email_data


@app.route('/emails')
def show_emails():
    emails = fetch_emails()
    return render_template('emails.html', emails=emails)


if __name__ == '__main__':
    app.run(debug=True)
