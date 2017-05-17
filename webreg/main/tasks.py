import urllib.request as request
from urllib.parse import urlencode
from celery import task
from django.core.mail.message import EmailMessage
from django.conf import settings


@task
def send_sms(params):
    url = getattr(settings, 'SMS_URL')
    if url:
        response = request.urlopen(url + '&' + urlencode(params))
        return response.getcode()
    return None
