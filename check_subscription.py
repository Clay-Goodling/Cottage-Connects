#! /usr/local/bin/python3.8

import utils

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def check_sub():
    sub_auth = utils.get_auth('subscribe_auth.json')
    messages = utils.get_mail(sub_auth, subscribers_only=False)

    for msg in messages:
        _, sender_address = utils.parse_address(msg['from'])
        if not sender_address:
            continue

        utils.add_subscriber(sender_address)

        response = MIMEMultipart('alternative')
        response['subject'] = 'Cottage Connects Subscription'
        response['from'] = sub_auth['email']
        response['to'] = sender_address

        text_part = utils.fill_template('sub.txt', {})
        html_part = utils.fill_template('sub.html', {})

        response.attach(MIMEText(text_part, 'text'))
        response.attach(MIMEText(html_part, 'html'))

        utils.send_mail(sender_address, response, sub_auth)


def check_unsub():
    unsub_auth = utils.get_auth('unsubscribe_auth.json')
    messages = utils.get_mail(unsub_auth, subscribers_only=False)

    for msg in messages:
        _, sender_address = utils.parse_address(msg['from'])
        if not sender_address:
            continue

        utils.remove_subscriber(sender_address)

        response = MIMEMultipart('alternative')
        response['subject'] = 'Cottage Connects Subscription'
        response['from'] = unsub_auth['email']
        response['to'] = sender_address

        text_part = utils.fill_template('unsub.txt', {})
        html_part = utils.fill_template('unsub.html', {})

        response.attach(MIMEText(text_part, 'text'))
        response.attach(MIMEText(html_part, 'html'))

        utils.send_mail(sender_address, response, unsub_auth)

    
if __name__ == '__main__':
    check_sub()
    check_unsub()
