from datetime import datetime, timedelta
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import pytz


def send_email(subject, html_body, to_emails):
    message = Mail(
        from_email=settings.FROM_ADDRESS,
        to_emails=to_emails,
        subject=subject,
        html_content=html_body
    )
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    response = sg.send(message)
    return response


def twentyfourhoursfromnow():
    """ Helper function for getting datetime 1 day from now
    """
    utc=pytz.UTC
    return utc.localize(datetime.now()) + timedelta(1)


def oneweekfromnow():
    """ Helper function for getting datetime 1 week from now
    """
    utc=pytz.UTC
    return utc.localize(datetime.now()) + timedelta(7)

def yesterday():
    """ Helper function for getting datetime from yesterday
    """
    utc=pytz.UTC
    return utc.localize(datetime.now()) + timedelta(-1)

special_chars = [
    '!',
    '@',
    '#',
    '$',
    '%',
    '^',
    '&',
    '*',
    '(',
    ')',
    '~',
    ';',
    ':',
    '<',
    '>',
    '"',
    '?',
    '/',
    "'",
    '[',
    ']',
    '|',
    '\\'
    '-',
    '_',
    '{',
    '}',
]
