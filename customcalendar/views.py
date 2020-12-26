import json
import logging
import os
from datetime import datetime
from mimetypes import guess_type

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.encoding import smart_str
from dndhelper import views as main_views

from customcalendar import modelgetters
from customcalendar.forms import calendarsettingsform


# Create your views here.
def generalJSONAnswerSuccess():
    return {'status': 'success'}

def generalJSONAnswerFailed():
    return {'status': 'failed'}

@login_required( login_url = 'login' )
def calendarHomePage(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = {}
    data['create_events'] = False
    data['PAGE_TITLE'] = 'Calendar home page: ' + settings.SOFTWARE_NAME_SHORT
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    data['needquillinput'] = False
    return render(request, 'views/calendar.html', data, content_type='text/html')

@login_required(login_url='login')
def calendarSettingsPage(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = {}
    data['create_events'] = False
    data['PAGE_TITLE'] = 'Wiki home page: ' + settings.SOFTWARE_NAME_SHORT
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    data['needquillinput'] = False
    return render(request, 'views/calendar_settings.html', data, content_type='text/html')

@login_required( login_url = 'login' )
def calendarSettingsGeneralAjaxRequest(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    result = generalJSONAnswerFailed()
    try:
        if request.method == "POST":
            result = calendarsettingsform.CCalendarFormParser(request)
        elif request.method == "GET": 
            data = modelgetters.get_calendar_settings()
            if data is not None:
                result = generalJSONAnswerSuccess()
                result['calendar'] = data 
    except Exception as e:
        logging.error(e)
    success = result['status'] == 'success'
    if success:
        return JsonResponse(result, status=200, safe=False)
    else:
        return JsonResponse(result, status=404, safe=False)


@login_required( login_url = 'login' )
def calendarSettingsMonthAjaxRequest(request, monthid=None):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    result = generalJSONAnswerFailed()
    try:
        if request.method == "POST":
            result = calendarsettingsform.CMonthFormParser(request)
        elif request.method == "GET": 
            data = modelgetters.get_month_settings(monthid=monthid)
            if data is not None:
                result = generalJSONAnswerSuccess()
                result['calendar'] = data 
    except Exception as e:
        logging.error(e)
    success = result['status'] == 'success'
    if success:
        return JsonResponse(result, status=200, safe=False)
    else:
        return JsonResponse(result, status=404, safe=False)


@login_required( login_url = 'login' )
def calendarSettingsWeekAjaxRequest(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    result = generalJSONAnswerFailed()
    try:
        if request.method == "GET": 
            data = modelgetters.get_week_settings()
            if data is not None:
                result = generalJSONAnswerSuccess()
                result['calendar'] = data 
    except Exception as e:
        logging.error(e)
    success = result['status'] == 'success'
    if success:
        return JsonResponse(result, status=200, safe=False)
    else:
        return JsonResponse(result, status=404, safe=False)


@login_required( login_url = 'login' )
def calendarSettingsWeekDayAjaxRequest(request, weekdayid=None):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    result = generalJSONAnswerFailed()
    try:
        if request.method == "POST":
            result = calendarsettingsform.CWeekDayFormParser(request)
        elif request.method == "GET":
            data = modelgetters.get_week_day_settings(weekdayid=weekdayid)
            if data is not None:
                result = generalJSONAnswerSuccess()
                result['calendar'] = data 
    except Exception as e:
        logging.error(e)
    success = result['status'] == 'success'
    if success:
        return JsonResponse(result, status=200, safe=False)
    else:
        return JsonResponse(result, status=404, safe=False)
