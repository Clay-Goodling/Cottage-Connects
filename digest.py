#! /usr/local/bin/python3.8

import datetime
import utils

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def build_header(date, messages):
  header = MIMEMultipart('alternative')

  text_contents = ''
  html_contents = '<ol>\n'
  for index, msg in enumerate(messages):
    subject = msg['subject']
    sender_name, sender_address = utils.parse_address(msg['from'])

    text_contents += '{}: {} - {} <{}>'.format(
      index + 1, subject, sender_name, sender_address)
    html_contents += '<li><a href="#{}">{}</a> - {} &lt{}&gt</li>\n'.format(
      index + 1, subject, sender_name, sender_address)
  html_contents += '</ol>\n'

  text_header = utils.fill_template('header.txt', {
    'date': date,
    'table_of_contents': text_contents
  })
  html_header = utils.fill_template('header.html', {
    'date': date,
    'table_of_contents': html_contents 
  })

  header.attach(MIMEText(text_header, 'text'))
  header.attach(MIMEText(html_header, 'html'))

  return header


def build_post_header(index, message):
  post_header = MIMEMultipart('alternative')

  subject = message['subject']
  sender_name, sender_address = utils.parse_address(message['from'])

  text = utils.fill_template('post_header.txt', {
    'index': str(index + 1),
    'subject': subject,
    'sender_name': sender_name,
    'sender_address': sender_address
  })
  html = utils.fill_template('post_header.html', {
    'index': str(index + 1),
    'subject': subject,
    'sender_name': sender_name,
    'sender_address': sender_address
  })

  post_header.attach(MIMEText(text, 'text'))
  post_header.attach(MIMEText(html, 'html'))

  return post_header


def build_post_footer(message):
  subject = message['subject']
  if subject[:4].lower() == 're: ':
    reply_subject = subject 
  else:
    reply_subject = 'Re: ' + subject
  sender_name, sender_address = utils.parse_address(message['from'])

  return MIMEText(utils.fill_template('post_footer.html', {
      'sender_address': sender_address,
      'reply_subject': reply_subject 
    }), 'html'
  )


def build_footer():
  footer = MIMEMultipart('alternative')

  text_footer = utils.fill_template('footer.txt', {})
  html_footer = utils.fill_template('footer.html', {})

  footer.attach(MIMEText(text_footer, 'text'))
  footer.attach(MIMEText(html_footer, 'html'))

  return footer


def build_no_messages(date):
  digest = MIMEMultipart('alternative')

  text = utils.fill_template('no_messages.txt', {
    'date': date
  })
  html = utils.fill_template('no_messages.html', {
    'date': date
  })

  digest.attach(MIMEText(text, 'text'))
  digest.attach(MIMEText(html, 'html'))

  return digest


def build_digest(date, messages, auth):

  digest = MIMEMultipart()
  digest['subject'] = 'Cottage Connects - ' + date
  digest['from'] = auth['email']
  digest['to'] = auth['email']

  if len(messages) == 0:
    digest.attach(build_no_messages(date))
    return digest

  digest.attach(build_header(date, messages))

  for index, msg in enumerate(messages):
    digest.attach(build_post_header(index, msg))
    digest.attach(msg)
    digest.attach(build_post_footer(msg))

  digest.attach(build_footer())

  return digest


def main():
  date = datetime.date.today().strftime('%B %d, %Y')
  auth = utils.get_auth()
  subscribed = utils.get_subscribed()

  messages = utils.get_mail(auth)
  digest = build_digest(date, messages, auth)
  utils.send_mail(subscribed, digest, auth)
  
  with open('history/' + date, 'w') as f:
    f.write(digest.as_string())


if __name__ == '__main__':
  main()
