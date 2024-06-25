import os
from flask import Flask, render_template
from email_client import fetch_emails_imap, fetch_emails_pop3

app = Flask(__name__)

username = os.getenv('GMAIL_USERNAME')
password = os.getenv('GMAIL_PASSWORD')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/emails/imap')
def show_emails_imap():
    emails = fetch_emails_imap(username, password)
    return render_template('emails.html', emails=emails)


@app.route('/emails/pop3')
def show_emails_pop3():
    emails = fetch_emails_pop3(username, password)
    return render_template('emails.html', emails=emails)


if __name__ == '__main__':
    app.run(debug=True)

