import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, unquote

import pytz
from customcalendar.models.calendarevent import CEvent
from dateutil import parser
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import DefaultStorage
from django.db import models
from django.urls import reverse
from permissions.models.permissions import Permission
from utils.usefull_functions import time_now


class PermissionCEvent(Permission):
    event = models.ForeignKey(CEvent, on_delete=models.CASCADE, null=False, blank=False, related_name='permissions')

    def json(self) -> dict:
        return {
            'grantedto': self.grantedto.get_username() if self.grantedto is not None else None,
            'createdon': self.createdon.isoformat(),
            'createdby': self.createdby.get_username() if self.createdby is not None else None,
            'permlevel': self.accesslevel,
            'event': str(self.event.unid)
        }

    @staticmethod
    def get(user:User, event:CEvent, currentuser:User):
        try: 
            if not event.permissionsable(currentuser):
                return None
            result = PermissionCEvent.objects.get(grantedto=user, event = event)
            if not (result is None):
                return result
        except Exception:
            pass
        return PermissionCEvent(createdby=currentuser, grantedto=user, event=event)

    @staticmethod
    def fromjson(jsonobj:dict, event:CEvent, commit:bool=False):
        try: 
            if event is None:
                return None
            if not 'grantedto' in jsonobj:
                return None
            if not 'permlevel' in jsonobj:
                return None 
            crby = None
            grto = None
            perml = 0
            try:
                perml = int(jsonobj['permlevel'])
                grto = User.objects.get(username = jsonobj['grantedto'])
            except Exception as exc:
                logging.error(exc)
                return None
            if 'createdby' in jsonobj:
                try:
                    user = User.objects.get(username=jsonobj['createdby'])
                    crby = user
                except Exception:
                    pass
            result = PermissionCEvent.get(grto, event, crby)
            result.accesslevel = perml
            if commit:
                result.save()
            return result
        except Exception as exc:
            pass
        return None
