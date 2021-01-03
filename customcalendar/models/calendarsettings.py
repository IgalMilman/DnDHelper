import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, unquote

import pytz
from crum import get_current_user
from dateutil import parser
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import DefaultStorage
from django.db import models
from django.urls import reverse


class CCalendar(models.Model):
    firstyear = models.IntegerField(verbose_name='First year')
    currentday = models.IntegerField(verbose_name='Current Day')
    currentmonth = models.IntegerField(verbose_name='Current Month')
    currentyear = models.IntegerField(verbose_name='Current Year')

    def number_of_month_year(self):
        return len(self.months.all())

    def number_of_days_year(self):
        result = 0
        for month in self.months.all():
            result+=month.numberofdays
        return result

    def number_of_days_week(self):
        return len(self.get_week().days.all())

    def create_week(self):
        week = CWeek(calendar = self)
        week.save()
        return week

    def get_week(self):
        if not hasattr(self, 'week'):
            week = self.create_week()
            return week
        return self.week

    def full_data_perm(self)->dict:
        result = self.full_data()
        return result

    def full_data(self)->dict:
        result = self.short_data()
        result['months'] = []
        for month in self.months.all():
            result['months'].append(month.full_data())
        result['week'] = self.get_week().full_data()
        return result
    
    def short_data(self)->dict:
        return {
            'firstyear': self.firstyear,
            'curday': self.currentday,
            'curmonth': self.currentmonth,
            'curyear': self.currentyear,
            'dpy': self.number_of_days_year(),
            'dpw': self.number_of_days_week(),
            'mpy': self.number_of_month_year(),
            'id': self.id,
        }

    def months_array(self)->list:
        result = []
        for month in self.months.all().order_by('monthnumber'):
            result.append(month.as_tuple())
        return result

    
    @staticmethod
    def canedit(user:User)->bool:
        if user is None:
            user = get_current_user()
        if user is None:
            return False
        return user.is_superuser

class CMonth(models.Model):
    numberofdays = models.IntegerField(verbose_name='Number of days a month')
    monthnumber = models.IntegerField(verbose_name='Month number')
    monthname = models.CharField(verbose_name='Month name:', null=False, blank=False, max_length=30)
    calendar = models.ForeignKey(CCalendar, on_delete=models.CASCADE, verbose_name="Calendar settings", null=False, blank=False, related_name='months')

    def as_tuple(self):
        return (self.monthnumber, self.monthname)

    def full_data(self):
        result = self.short_data()
        return result
    
    def short_data(self):
        return {
            'numberofdays': self.numberofdays, 
            'monthnumber': self.monthnumber, 
            'monthname': self.monthname,
            'id': self.id,
        }

    def number_of_days(self):
        return self.numberofdays

class CWeek(models.Model):
    calendar = models.OneToOneField(CCalendar, on_delete=models.CASCADE, verbose_name="Calendar settings", primary_key=True, related_name='week')
   
    def full_data(self):
        result = self.short_data()
        result['days'] = []
        for day in self.days.all():
            result['days'].append(day.full_data())
        return result
    
    def short_data(self):
        return {
            'numberofdays': self.number_of_days(),
            'id':self.calendar.id,
        }
    
    def number_of_days(self):
        return len(self.days.all())

class CWeekDay(models.Model):
    dayname = models.CharField(verbose_name='Week day name:', null=False, blank=False, max_length=30)
    daynumber = models.IntegerField(verbose_name='Week day number')
    workday = models.BooleanField(verbose_name='Workday', default=True, null=False, blank=False)
    week = models.ForeignKey(CWeek, on_delete=models.CASCADE, verbose_name="Week settings", null=False, blank=False, related_name='days')
   
    def full_data(self):
        result = self.short_data()
        return result
    
    def short_data(self):
        return {
            'dayname': self.dayname,
            'daynumber': self.daynumber,
            'workday': self.workday,
            'id':self.id,
        }
