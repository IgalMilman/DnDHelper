import logging
from datetime import datetime

import pytz
from customcalendar.models import calendarsettings
from django import forms
from django.shortcuts import redirect, render
from django.urls import reverse
from dndhelper import settings
from dndhelper import views as main_views
from dndhelper.widget import form_switch, quill


class CCalendarForm(forms.ModelForm):
    class Meta:
        model = calendarsettings.CCalendar
        fields = ('firstyear', )

class CMonthForm(forms.ModelForm):
    class Meta:
        model = calendarsettings.CMonth
        fields = ('monthnumber', 'monthname', 'numberofdays', )

class CWeekDayForm(forms.ModelForm):
    class Meta:
        model = calendarsettings.CWeekDay
        fields = ('daynumber', 'dayname', 'workday', )

def CCalendarFormParser(request, forceaction=None):
    if not calendarsettings.CCalendar.canedit(request.user):
        return {'status': 'failed', 'message': 'No permissions to edit'}
    if (request.method != 'POST') or not ('action' in request.POST):
        return {'status': 'failed', 'message': 'Wrong request.'}
    if forceaction is None:
        forceaction = request.POST['action']
    if (forceaction=='add'):
        form = CCalendarForm(request.POST)
        if form.is_valid():
            try:
                model = form.save(commit=False)
                model.save()
                return {'status': 'success', 'message': 'Created successfully'}
            except Exception as e:
                logging.error(e)
    elif (forceaction=='changed'):
        if('targetid' in request.POST):
            try:
                curcalendar=calendarsettings.CCalendar.objects.get(id=request.POST['targetid'])
            except Exception as e:
                logging.error(e)
            if curcalendar is not None:
                try:
                    form = CCalendarForm(request.POST, instance=curcalendar)
                    model = form.save(commit=False)
                    model.save()
                    return {'status': 'success', 'message': 'Data saved'}
                except Exception as e:
                    logging.error(e)
            else:
                return CCalendarFormParser(request, forceaction='add')
    elif (forceaction=='delete'): 
        if('targetid' in request.POST):
            try:
                curcalendar=calendarsettings.CCalendar.objects.get(id=request.POST['targetid'])
            except Exception as e:
                logging.error(e)
            try:
                curcalendar.delete()
                return {'status': 'success', 'message': 'Deleted successfully'}
            except Exception as e:
                logging.error(e)
    return {'status': 'failed', 'message': 'Failed to save the data'}

def CMonthFormParser(request, forceaction=None):
    if not calendarsettings.CCalendar.canedit(request.user):
        return {'status': 'failed', 'message': 'No permissions to edit'}
    if (request.method != 'POST') or not ('action' in request.POST):
        return {'status': 'failed', 'message': 'Wrong request.'} 
    if forceaction is None:
        forceaction = request.POST['action']
    cal = None
    if 'calid' in request.POST:
        try:
            calid = request.POST['calid']
            if isinstance(calid, list):
                calid=calid[0]
            cal = calendarsettings.CCalendar.objects.get(id=request.POST['calid'])
        except Exception as e:
            logging.error(e)
    if cal is None:
        return {'status': 'failed', 'message': 'Wrong request.'}
    if (forceaction=='add'):
        form = CMonthForm(request.POST)
        if form.is_valid():
            try:
                model = form.save(commit=False)
                model.calendar = cal
                model.save()
                return {'status': 'success', 'message': 'Created successfully'}
            except Exception as e:
                logging.error(e)
    elif (forceaction=='changed'):
        if('targetid' in request.POST):
            try:
                curmonth=calendarsettings.CMonth.objects.get(id=request.POST['targetid'])
            except Exception as e:
                logging.error(e)
            if curmonth is not None:
                try:
                    form = CMonthForm(request.POST, instance=curmonth)
                    model = form.save(commit=False)
                    model.save()
                    return {'status': 'success', 'message': 'Data saved'}
                except Exception as e:
                    logging.error(e)
            else:
                return CMonthFormParser(request, forceaction='add')
    elif (forceaction=='delete'): 
        if('targetid' in request.POST):
            try:
                curmonth=calendarsettings.CMonth.objects.get(id=request.POST['targetid'])
            except Exception as e:
                logging.error(e)
            try:
                curmonth.delete()
                return {'status': 'success', 'message': 'Deleted successfully'}
            except Exception as e:
                logging.error(e)
    return {'status': 'failed', 'message': 'Failed to save the data'}

def CWeekDayFormParser(request, forceaction=None):
    if not calendarsettings.CCalendar.canedit(request.user):
        return {'status': 'failed', 'message': 'No permissions to edit'}
    if (request.method != 'POST') or not ('action' in request.POST):
        return {'status': 'failed', 'message': 'Wrong request.'}
    if forceaction is None:
        forceaction = request.POST['action']
    cal = None
    if 'calid' in request.POST:
        try:
            calid = request.POST['calid']
            if isinstance(calid, list):
                calid=calid[0]
            cal = calendarsettings.CCalendar.objects.get(id=request.POST['calid'])
        except Exception as e:
            logging.error(e)
    if cal is None:
        return {'status': 'failed', 'message': 'Wrong request.'}
    week = cal.get_week()
    if week is None:
        return {'status': 'failed', 'message': 'Wrong request. No week like this.'} 
    if (forceaction=='add'):
        form = CWeekDayForm(request.POST)
        if form.is_valid():
            try:
                model = form.save(commit=False)
                model.week = week
                model.save()
                return {'status': 'success', 'message': 'Created successfully'}
            except Exception as e:
                logging.error(e)
    elif (forceaction=='changed'):
        if('targetid' in request.POST):
            try:
                curweekday=calendarsettings.CWeekDay.objects.get(id=request.POST['targetid'])
            except Exception as e:
                logging.error(e)
            if curweekday is not None:
                try:
                    form = CWeekDayForm(request.POST, instance=curweekday)
                    model = form.save(commit=False)
                    model.save()
                    return {'status': 'success', 'message': 'Data saved'}
                except Exception as e:
                    logging.error(e)
            else:
                return CWeekDayFormParser(request, forcemethod='add')
    elif (forceaction=='delete'): 
        if('targetid' in request.POST):
            try:
                curweekday=calendarsettings.CWeekDay.objects.get(id=request.POST['targetid'])
            except Exception as e:
                logging.error(e)
            try:
                curweekday.delete()
                return {'status': 'success', 'message': 'Deleted successfully'}
            except Exception as e:
                logging.error(e)
    return {'status': 'failed', 'message': 'Failed to save the data'}

