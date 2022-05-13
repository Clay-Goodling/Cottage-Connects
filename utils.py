import imaplib
import json
import re
import smtplib

from email.parser import BytesParser


def get_mail(auth, subscribers_only=True):
  subscribed = get_subscribed()

  imap = imaplib.IMAP4_SSL(auth['imaphost'])
  imap.login(auth['email'], auth['pass'])

  imap.select('Inbox')
  rsp, data = imap.search(None, 'UNSEEN')
  if rsp != 'OK':
    return []

  msns = data[0].split(b' ')
  if msns[0] == b'':
    return []

  messages = []
  parser = BytesParser()
  for msn in msns:
    rsp, data = imap.fetch(msn, '(RFC822)')
    if rsp != 'OK':
      continue
    msg = parser.parsebytes(data[0][1])

    _, sender_address = parse_address(msg['from'])
    if sender_address in subscribed or not subscribers_only:
      messages.append(msg)

  return messages


def send_mail(recipients, message, auth):
  with smtplib.SMTP(auth['smtphost'], auth['smtpport']) as s:
    s.ehlo()
    s.starttls()
    s.login(auth['email'], auth['pass'])
    s.sendmail(auth['email'], recipients, message.as_string())


def get_auth(auth_file='auth.json'):
  with open(auth_file, 'r') as f:
    return json.load(f)


def get_subscribed():
  with open('subscribed.json', 'r') as f:
    return json.load(f)


def add_subscriber(email):
  subscribers = get_subscribed()
  if email not in subscribers:
    subscribers.append(email)
  with open('subscribed.json', 'w') as f:
    f.write(json.dumps(subscribers))


def remove_subscriber(email):
  subscribers = get_subscribed()
  subscribers = [s for s in subscribers if s != email]
  with open('subscribed.json', 'w') as f:
    f.write(json.dumps(subscribers))


def parse_address(addr):
  match = re.search(r'(.*)<(.*)>$', addr)
  if match:
    name = match.group(1)
    address = match.group(2)
    return name, address
  else:
    return '', ''


def fill_template(template, dict):
  with open('templates/' + template, 'r') as f:
    s = f.read()

  pattern = r'{\s*([a-zA-Z0-9\-\_]*)\s*}'
  return re.sub(pattern, lambda x: dict.get(x.group(1), ''), s)
