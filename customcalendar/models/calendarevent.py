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
from permissions.models.permissions import (PERMISSION_LEVELS_DICTIONARY,
                                            Permission)
from utils.usefull_functions import time_now
from utils.widget import quill

EVENT_TYPES_DICTIONARY = {"History event":0, "Holiday":10, "Party event": 20, "Personal event": 30}
EVENT_TYPES_NUMBER_DICTIONARY = {0:"History event", 10:"Holiday", 20:"Party event", 30:"Personal event"}
EVENT_TYPES_TUPLES = [(0, "History event"), (10, "Holiday"), (20, "Party event"), (30, "Personal event")]

class CEvent(models.Model):
    unid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    eventday = models.IntegerField(verbose_name='Event Day', null=False, blank=False)
    eventmonth = models.IntegerField(verbose_name='Event Month', null=False, blank=False)
    eventyear = models.IntegerField(verbose_name='Event Year', null=False, blank=False)
    createdon = models.DateTimeField("Created time", auto_now_add=True, null=False, blank=False)
    updatedon = models.DateTimeField("Updated time", auto_now_add=True, null=False, blank=False)
    createdby = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Created by", null=True, blank=True, related_name='createdcalendarevents')
    updatedby = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Updated by", null=True, blank=True, related_name='lastupdatedcalendarevents')
    commonknowledge = models.BooleanField("Is common knowledge?", default=False)
    eventtype = models.IntegerField("Event Types", choices=EVENT_TYPES_TUPLES, null=False, blank=False, default=0)
    title = models.CharField("Title*", max_length=160, null=False, blank=False)
    text = models.TextField("Article text", null=True, blank=True)

    def save(self, *args, **kwargs):
        folder = self.get_files_folder()
        if folder is not None:
            self.text = quill.save_images_from_quill(self.text, folder, self.get_files_link())
        super(CEvent, self).save(*args, **kwargs)

    def createtime(self) -> datetime:
        return self.createdon.astimezone(pytz.timezone('America/New_York'))

    def updatetime(self) -> datetime:
        return self.updatedon.astimezone(pytz.timezone('America/New_York'))

    def createuser(self) -> str:
        if (self.createdby is None):
            return None
        return self.createdby.get_full_name()

    def updateuser(self):
        if (self.updatedby is None):
            return None
        return self.updatedby.get_full_name()

    def date_hash(self)->str:
        return str(self.eventyear) + '-' + str(self.eventmonth) + '-' + str(self.eventday)

    def get_date(self)->str:
        return str(self.eventyear) + '-' + str(self.eventmonth) + '-' + str(self.eventday)
    
    def __str__(self) -> str:
        return "Calendar event: " + str(self.title) + ". UNID: " + str(self.unid)

    def is_quill_content(self) -> bool:
        if self.text is None:
            return False
        return quill.check_quill_string(self.text)

    def get_quill_content(self) -> str:
        if self.text is None:
            return ''
        return quill.get_quill_text(self.text, files_link=self.get_files_link())

    def get_quill_content_simple(self, number_of_lines=1) -> str:
        if self.text is None:
            return ''
        return quill.get_quill_text_simple(self.text, number_of_lines=number_of_lines)

    def get_content(self) -> str:
        if self.text is None:
            return ''
        return self.text

    def get_file(self, filename):
        if os.path.exists(os.path.join(self.get_files_folder(), filename)):
            file = open(os.path.join(self.get_files_folder(), filename), 'rb')
            res = file.read()
            file.close()
            return res
        return None

    def get_files_folder(self) -> str:
        try:
            folder_path = os.path.join(settings.CALENDAR_EVENT_FOLDER, str(self.unid))
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            return folder_path
        except Exception:
            return None
       
    def generate_link(self) -> str:
        return self.get_link()

    def get_link(self) -> str:
        return reverse('calendar_event_page', kwargs={'ceventuuid': self.unid})

    def get_link_calendar(self) -> str:
        return reverse('calendar_homepage') + '#' + self.date_hash()
       
    def get_data_link(self) -> str:
        return reverse('calendar_event_api', kwargs={'ceventuuid': self.unid})
       
    def get_files_link(self) -> str:
        return reverse('calendar_event_page_file_empty', kwargs={'ceventuuid': self.unid})

    def anchor_id(self) -> str:
        return 'a'+str(self.unid)

    def editable(self, user:User=None) -> bool:
        if user is None:
            user = get_current_user()
        if user is None:
            return False
        if user.is_superuser:
            return True
        try:
            permissionlevel = self.permissions.get(grantedto=user)
            if permissionlevel is None:
                return False
            return permissionlevel.accesslevel >= PERMISSION_LEVELS_DICTIONARY['Edit']
        except Exception:
            return False

    def permissionsable(self, user:User=None) -> bool:
        if user is None:
            user = get_current_user()
        if user is None:
            return False
        if user.is_superuser:
            return True
        try:
            permissionlevel = self.permissions.get(grantedto=user)
            if permissionlevel is None:
                return False
            return permissionlevel.accesslevel >= PERMISSION_LEVELS_DICTIONARY['Permissions']
        except Exception:
            return False

    def viewable(self, user:User=None) -> bool:
        if user is None:
            user = get_current_user()
        if user is None:
            return False
        if user.is_superuser:
            return True
        if self.commonknowledge:
            return True
        try:
            if self.commonknowledge:
                return True
            permissionlevel = self.permissions.get(grantedto=user)
            if permissionlevel is not None:
                return permissionlevel.accesslevel >= PERMISSION_LEVELS_DICTIONARY['View Only']
        except Exception:
            pass
        return False

    def permission_list(self) -> list:
        result = []
        for perm in self.permissions.all():
            result.append(perm.json())
        return result

    def json(self):
        return {
            'unid': str(self.unid),
            'createdon': self.createdon.isoformat(),
            'createdby': self.createdby.get_username() if self.createdby is not None else None,
            'updatedon': self.updatedon.isoformat(),
            'updatedby': self.updatedby.get_username() if self.updatedby is not None else None,
            'commonknowledge': self.commonknowledge,
            'title': self.title,
            'year': self.eventyear,
            'month': self.eventmonth,
            'day': self.eventday,
            'text': json.loads(self.text) if self.is_quill_content() else quill.quillify_text(self.text),
            'perm': self.permission_list()
        }

    def shortjson(self):
        return {
            'unid': str(self.unid),
            'title': self.title,
            'year': self.eventyear,
            'month': self.eventmonth,
            'day': self.eventday,
            'apilink': self.get_data_link(),
            'directlink': self.get_link()
        }

    def jsondata(self):
        return {
            'unid': str(self.unid),
            'title': self.title,
            'year': self.eventyear,
            'month': self.eventmonth,
            'day': self.eventday,
            'text': self.get_quill_content(),
            'apilink': self.get_data_link(),
            'directlink': self.get_link()
        }
    
    @staticmethod
    def fromjson(jsonobject:dict, commit:bool = False, override:bool = False):
        result = CEvent()
        if not ('title' in jsonobject):
            return None
        tmp = None
        if 'unid' in jsonobject:
            try:
                result.unid = uuid.UUID(jsonobject['unid'])
                try:
                    tmp = CEvent.objects.get(unid = result.unid)
                    if (tmp is not None) and not override:
                        return None
                except Exception:
                    pass
            except Exception:
                pass
        if 'createdon' in jsonobject:
            try:
                result.createdon = parser.parse(jsonobject['createdon'])
            except Exception:
                pass
        if 'updatedon' in jsonobject:
            try:
                result.updatedon = parser.parse(jsonobject['updatedon'])
            except Exception:
                pass
        if 'createdby' in jsonobject:
            try:
                user = User.objects.get(username=jsonobject['createdby'])
                result.createdby = user
            except Exception:
                pass
        if 'updatedby' in jsonobject:
            try:
                user = User.objects.get(username=jsonobject['updatedby'])
                result.updatedby = user
            except Exception:
                pass
        if 'commonknowledge' in jsonobject:
            try:
                result.commonknowledge = bool(jsonobject['commonknowledge'])
            except Exception:
                pass
        if 'title' in jsonobject:
            try:
                result.title = str(jsonobject['title'])
            except Exception:
                pass
        if 'text' in jsonobject:
            try:
                result.text = json.dumps(jsonobject['text'])
            except Exception:
                pass
        try:
            if commit:
                if tmp is not None:
                    tmp.delete()
                result.save()
            perms = []
            if 'perm' in jsonobject:
                try:
                    from customcalendar.models.permissionevent import \
                        PermissionCEvent
                    for perm in jsonobject['perm']:
                        perms.append(PermissionCEvent.fromjson(perm, result, commit=commit))
                except Exception:
                    pass 
            return {'event': result, 'perm': perms}
        except Exception as exc:
            return None
        return None

    @staticmethod
    def cancreate(user:User)->bool:
        if user is None:
            user = get_current_user()
        if user is None:
            return False
        #return user.is_superuser
        return True

    @staticmethod
    def create_types(user:User, event=None)->list:
        if user is None:
            user = get_current_user()
        if user is None:
            return False
        if user.is_superuser:
            return EVENT_TYPES_TUPLES
        if event is None:
            return EVENT_TYPES_TUPLES[2:]
        else:
            result = EVENT_TYPES_TUPLES[2:]
            for i in EVENT_TYPES_TUPLES:
                if i[0] == event.eventtype:
                    result = [i]+result
                    return result
            return result
        

    @staticmethod
    def get_all_year_events(year:int, user:User)->list:
        if user is None:
            user = get_current_user()
        if user is None:
            return []
        allevents = CEvent.objects.filter(eventyear=year)
        result = []
        for event in allevents:
            if event.viewable(user):
                result.append(event)
        return result
