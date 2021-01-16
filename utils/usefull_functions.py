import json
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse

import pytz
from django.shortcuts import render


def generalJSONAnswerSuccess():
    return {'status': 'success'}

def generalJSONAnswerFailed():
    return {'status': 'failed'}

def time_now(instance=None):
    return datetime.now(pytz.utc)

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
