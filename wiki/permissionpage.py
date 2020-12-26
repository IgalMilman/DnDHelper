import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, unquote
import logging

import pytz
from dateutil import parser
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import DefaultStorage
from django.db import models
from django.urls import reverse
from permissions import permissions

from wiki.wikipage import WikiPage


def time_now(instance=None):
    return datetime.now(pytz.utc)

class PermissionPage(permissions.Permission):
    wikipage = models.ForeignKey(WikiPage, on_delete=models.CASCADE, null=False, blank=False, related_name='permissions')

    def json(self) -> dict:
        return {
            'grantedto': self.grantedto.get_username() if self.grantedto is not None else None,
            'createdon': self.createdon.isoformat(),
            'createdby': self.createdby.get_username() if self.createdby is not None else None,
            'permlevel': self.accesslevel,
            'wikipage': str(self.wikipage.unid)
        }

    @staticmethod
    def get(user:User, wikipage:WikiPage, currentuser:User):
        try: 
            if not wikipage.permissionsable(currentuser):
                return None
            result = PermissionPage.objects.get(grantedto=user, wikipage = wikipage)
            if not (result is None):
                return result
        except Exception:
            pass
        return PermissionPage(createdby=currentuser, grantedto=user, wikipage=wikipage)

    @staticmethod
    def fromjson(jsonobj:dict, wikipage:WikiPage, commit:bool=False):
        try: 
            if wikipage is None:
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
            result = PermissionPage.get(grto, wikipage, crby)
            result.accesslevel = perml
            # if 'createdon' in jsonobj:
            #     try:
            #         result.createdon = parser.parse(jsonobj['createdon'])
            #     except Exception:
            #         pass
            if commit:
                result.save()
            return result
        except Exception as exc:
            pass
        return None
