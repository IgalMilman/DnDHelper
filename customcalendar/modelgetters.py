import logging

from customcalendar.models.calendarsettings import (CCalendar, CMonth, CWeek,
                                                    CWeekDay)

def get_calendar(calid:int=None):
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
            cal = CCalendar(firstyear = 0)
            cal.save()
    except Exception as e:
        logging.error('Failed to create new calendar: ' + str(e))
    return cal

def get_calendar_settings(calid:int=None):
    cal = get_calendar(calid=calid)
    if cal is None:
        return None
    return cal.full_data()

def get_month_settings(calid:int=None, monthid:int=None):
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

def get_week_settings(calid:int=None):
    cal = get_calendar(calid=calid)
    if cal is None:
        return None
    week = cal.get_week()
    if week is None:
        return None
    return week.full_data()

def get_week_day_settings(calid:int=None, weekdayid:int=None):
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