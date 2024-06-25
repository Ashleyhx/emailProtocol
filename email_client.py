import imaplib
import poplib
import email
from email.header import decode_header


def fetch_emails_imap(username, password):
    imap_url = 'imap.gmail.com'
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(username, password)
    mail.select('inbox')

    res, messages = mail.select('inbox')
    messages = int(messages[0])
    n = 3
    email_data = []

    for i in range(messages, messages - n, -1):
        res, msg = mail.fetch(str(i), '(RFC822)')
        email_data.extend(parse_email(msg))

    mail.logout()
    return email_data


def fetch_emails_pop3(username, password):
    pop3_url = 'pop.gmail.com'
    mail = poplib.POP3_SSL(pop3_url)
    mail.user(username)
    mail.pass_(password)

    num_messages = len(mail.list()[1])
    n = min(num_messages, 3)
    email_data = []

    for i in range(num_messages, num_messages - n, -1):
        msg = mail.retr(i)[1]
        msg = b"\n".join(msg).decode()
        msg = email.message_from_string(msg)
        email_data.append(parse_single_email(msg))

    mail.quit()
    return email_data


def parse_email(messages):
    email_data = []
    for response in messages:
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1])
            email_data.append(parse_single_email(msg))
    return email_data


def parse_single_email(msg):
    From = decode_header(msg['From'])[0][0]
    From = From.decode() if isinstance(From, bytes) else From

    subject = decode_header(msg['Subject'])[0][0]
    subject = subject.decode() if isinstance(subject, bytes) else subject

    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            charset = part.get_content_charset()
            if part.get_content_type() == 'text/plain':
                payload = part.get_payload(decode=True)
                try:
                    body = payload.decode(charset if charset else 'utf-8', errors='replace')
                except LookupError:  # charset is not recognized
                    body = payload.decode('utf-8', errors='replace')
                break
    else:
        charset = msg.get_content_charset()
        payload = msg.get_payload(decode=True)
        try:
            body = payload.decode(charset if charset else 'utf-8', errors='replace')
        except LookupError:
            body = payload.decode('utf-8', errors='replace')

    return {'from': From, 'subject': subject, 'body': body}

