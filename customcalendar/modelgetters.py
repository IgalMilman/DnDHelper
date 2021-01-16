import logging

from crum import get_current_user
from django.contrib.auth.models import User

from customcalendar.models.calendarevent import CEvent
from customcalendar.models.calendarsettings import (CCalendar, CMonth, CWeek,
                                                    CWeekDay)


def get_calendar(calid:int=None)->CCalendar:
    cal = None
    try:
        if calid is None:
            cals = CCalendar.objects.all()
            if len(cals)>0:
                cal = cals[0]
        else:
            cal = CCalendar.objects.get(id=calid)
    except Exception as e:
        logging.error(e)
    try:
        if cal is None:
            cal = CCalendar(firstyear = 0, currentday=1, currentmonth=0, currentyear=0)
            cal.save()
    except Exception as e:
        logging.error('Failed to create new calendar: ' + str(e))
    return cal

def get_calendar_settings(calid:int=None, user:User=None)->dict:
    cal = get_calendar(calid=calid)
    if cal is None:
        return None
    tmp = cal.full_data()
    try:
        tmp['editable'] = CCalendar.canedit(user)
    except Exception as exc:
        logging.error(exc)
    return tmp


def get_month_settings(calid:int=None, monthid:int=None)->dict:
    cal = get_calendar(calid=calid)
    if cal is None:
        return None
    month = None
    try:
        if monthid is None:
            months = CMonth.objects.all()
            if len(months)>0:
                month = months[0]
        else:
            month = CMonth.objects.get(id=monthid)
    except Exception as e:
        logging.error(e)
    if month is None:
        return None
    return month.full_data()

def get_week_settings(calid:int=None)->dict:
    cal = get_calendar(calid=calid)
    if cal is None:
        return None
    week = cal.get_week()
    if week is None:
        return None
    return week.full_data()

def get_week_day_settings(calid:int=None, weekdayid:int=None)->dict:
    if weekdayid is None:
        return None
    cal = get_calendar(calid=calid)
    if cal is None:
        return None
    week = cal.get_week()
    if week is None:
        return None
    weekday = None
    try:
        weekday = week.days.get(id=weekdayid)
    except Exception as e:
        logging.error(e)
    if weekday is None:
        return None
    return weekday.full_data()

def get_one_event_page_data_api(ceventuuid, user)->dict:
    try:
        event = CEvent.objects.get(unid=ceventuuid)
        if (event is None):
            return None
        if (not event.viewable(user)):
            return None
        data={}
        res = event.jsondata()
        res['editable'] = event.editable(user)
        data['event'] = res
        return data
    except Exception as err:
        logging.error(err)
        return None

def get_one_event_page_data(ceventuuid, user)->dict:
    try:
        event = CEvent.objects.get(unid=ceventuuid)
        if (event is None):
            return None
        if (not event.viewable(user)):
            return None
        data={}
        data['event'] = event
        return data
    except Exception as err:
        logging.error(err)
        return None

def get_one_year_events(year:int, user:User) -> list:
    try:
        events = CEvent.get_all_year_events(year, user)
        result = []
        for event in events:
            result.append(event.shortjson())
        return result
    except Exception as err:
        logging.error(err)
        return []

def get_all_events(user:User=None)->list:
    try:
        if user is None:
            user = get_current_user()
        result = []
        events = CEvent.objects.all().order_by('-createdon')
        for event in events:
            if (event.viewable(user)):
                result.append(event)
    except Exception as err:
        return None
    return {'all_events': result}
