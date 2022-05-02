from django.http import HttpResponse
from django.shortcuts import render
import logging

logger = logging.getLogger('watchtower')
logger_console = logging.getLogger('console')

# Create your views here.
def index_view(request):
    logger.info("Index view visited")
    return HttpResponse("Hello")