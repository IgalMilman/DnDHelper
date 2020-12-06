import json, os, logging
from datetime import datetime
from urllib.parse import urlencode, urlparse, parse_qs
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import forms as userforms
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils.cache import patch_response_headers
from django.contrib.auth.decorators import login_required
from django.conf import settings
from dndhelper import registeruser
from dndhelper import accessability

def initRequest(request):
    """
    A function to check and verify request
    :param request:
    :return:
    """

    url = request.get_full_path()
    u = urlparse(url)
    query = parse_qs(u.query)
    query.pop('timestamp', None)
    try:
        u = u._replace(query=urlencode(query, True))
    except UnicodeEncodeError:
        data = {
            'errormessage': 'Error appeared while encoding URL!'
        }
        return False, render(request, json.dumps(data), content_type='text/html')

    ## Set default page lifetime in the http header, for the use of the front end cache
    request.session['max_age_minutes'] = 10

    ## Create a dict in session for storing request params
    requestParams = {}
    request.session['requestParams'] = requestParams
    if getattr(settings, 'SESSION_COOKIE_AGE', None):
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)

    if request.method == 'POST':
        for p in request.POST:
            pval = request.POST[p]
            pval = pval.replace('+', ' ')
            request.session['requestParams'][p.lower()] = pval
    else:
        for p in request.GET:
            pval = request.GET[p]
            pval = pval.replace('+', ' ')

            ## Here check if int or date type params can be placed

            request.session['requestParams'][p.lower()] = pval

    return True, None


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