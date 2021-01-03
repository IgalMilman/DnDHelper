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

from customcalendar import modelgetters, permissionresponse
from customcalendar.forms import calendarsettingsform,calendareventform,currentdatesettingform
from customcalendar.models.calendarevent import CEvent


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
    data['create_events'] = CEvent.cancreate(request.user)
    data['PAGE_TITLE'] = 'Calendar home page: ' + settings.SOFTWARE_NAME_SHORT
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    data['needquillinput'] = False
    return render(request, 'calendar/views/calendar.html', data, content_type='text/html')

@login_required( login_url = 'login' )
def calendarAllEventsPage(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = modelgetters.get_all_events(request.user)
    data['create_events'] = CEvent.cancreate(request.user)
    data['PAGE_TITLE'] = 'Calendar all events: ' + settings.SOFTWARE_NAME_SHORT
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    data['needquillinput'] = False
    return render(request, 'calendar/views/calendar_allevents.html', data, content_type='text/html')

@login_required( login_url = 'login' )
def calendarEventPage(request, ceventuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = modelgetters.get_one_event_page_data(ceventuuid, request.user)
    if (data is None) or not ('event' in data) or not isinstance(data['event'], CEvent):
        return redirect(reverse('calendar_homepage'))
    data['PAGE_TITLE'] = data['event'].title + ': ' + settings.SOFTWARE_NAME_SHORT
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    data['needquillinput'] = True
    return render(request, 'calendar/views/calendar_event.html', data, content_type='text/html')

@login_required( login_url = 'login' )
def calendarEventPageAPI(request, ceventuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = modelgetters.get_one_event_page_data_api(ceventuuid, request.user)
    if (data is None) or not ('event' in data) or not isinstance(data['event'], dict):
        return JsonResponse(generalJSONAnswerFailed(), status=404, safe=False)
    result = {**generalJSONAnswerSuccess(), **data}
    return JsonResponse(result, status=200, safe=False)

@login_required( login_url = 'login' )
def calendarAllEventsAPI(request, year):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    datalist = modelgetters.get_one_year_events(year, request.user)
    if datalist is None:
        return JsonResponse(generalJSONAnswerFailed(), status=404, safe=False)
    result = generalJSONAnswerSuccess()
    result['events'] = datalist
    return JsonResponse(result, status=200, safe=False)

@login_required( login_url = 'login' )
def calendarEventPageFile(request, ceventuuid, filename):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    try:
        event = CEvent.objects.get(unid=ceventuuid)
    except Exception:
        event = None
    if event is None:
        return HttpResponseNotFound("File was not found")
    filecontent = event.get_file(filename)
    if filecontent is None:
        return HttpResponseNotFound("File was not found")
    response = HttpResponse(filecontent, content_type=guess_type(filename)[0])
    return response

@login_required( login_url = 'login' )
def calendarEventPageForm(request):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    return calendareventform.CEventFormParse(request)

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
    return render(request, 'calendar/views/calendar_settings.html', data, content_type='text/html')

@login_required( login_url = 'login' )
def calendarSettingsGeneralAjaxRequest(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    result = generalJSONAnswerFailed()
    try:
        if request.method == "POST":
            result = calendarsettingsform.CCalendarForm(request)
        elif request.method == "GET":
            data = modelgetters.get_calendar_settings(None, request.user)
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
def calendarUpdateDateAjaxRequest(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    result = generalJSONAnswerFailed()
    try:
        if request.method == "POST":
            result = currentdatesettingform.CurDateFormParser(request)
        else:
            return JsonResponse(result, status=404, safe=False)
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

@login_required( login_url = 'login' )
def eventPermissionsAjaxRequestHandle(request, ceventuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    event = permissionresponse.get_event(request, ceventuuid)
    if event is None:
        return JsonResponse({'status': 'failed', 'message': 'wiki page not found'}, status=404, safe=False)
    data = permissionresponse.handle_permissions_request_event(request, event)
    if data is None:
        return JsonResponse({'status': 'failed', 'message': 'error in the query'}, status=406, safe=False)
    return JsonResponse(data, status=200, safe=False)