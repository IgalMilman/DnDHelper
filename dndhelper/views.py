import json
import logging
import os
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse

from django.conf import settings
from django.contrib.auth import forms as userforms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.cache import patch_response_headers
from utils.usefull_functions import initRequest

from dndhelper import accessability, changeuser, registeruser


def homepage(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {}
    data['PAGE_TITLE'] = settings.SOFTWARE_NAME
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    data['main_items'] = accessability.accessible_modules(request.user)
    return render(request, 'index.html', data, content_type='text/html')

def register(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    return registeruser.register(request)

@login_required( login_url = 'login' )
def userpersonalpage(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {}
    data['PAGE_TITLE'] = 'Personal page: '+settings.SOFTWARE_NAME_SHORT
    data['built'] = datetime.now().strftime("%H:%M:%S")
    return render(request, 'user/personal/main.html', data, content_type='text/html')

@login_required( login_url = 'login' )
def changeuserpage(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    return changeuser.changeUserFormParser(request)
