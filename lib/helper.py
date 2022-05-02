import requests
import json
from django.db.models import Q
from django.conf import settings
import datetime
import pytz
# from web_analytics.models import CustomEvent, EVENT_NAMES
#from payment.models import Coupon, Tax
#from courses.models import OurPlans
import logging

logger = logging.getLogger('watchtower')
logger_console = logging.getLogger('console')


def get_location_by_ip(ip_address):
    """Analytics data by Object type"""
    try:
        request_url = "http://ip-api.com/json/{}".format(ip_address)
        response = requests.get(request_url)
        json_response = response.json()
        return json_response
    except Exception as error:
        raise Exception({"get_location_by_ip: ": str(error)})


def get_client_ip(request):
    ip = ""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

