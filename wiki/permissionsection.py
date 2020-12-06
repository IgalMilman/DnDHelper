import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, unquote

import pytz
from dateutil import parser
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import DefaultStorage
from django.db import models
from django.urls import reverse
from permissions import permissions

from wiki import wikisection


def time_now(instance=None):
    return datetime.now(pytz.utc)

class PermissionSection(permissions.Permission):
    section = models.ForeignKey(wikisection.WikiSection, on_delete=models.CASCADE, null=False, blank=False, related_name='permissions')

    def json(self) -> dict:
        return {
            'grantedto': self.grantedto.get_username() if self.grantedto is not None else None,
            'createdon': self.createdon.isoformat(),
            'createdby': self.createdby.get_username() if self.createdby is not None else None,
            'permlevel': self.accesslevel,
            'section': str(self.section.unid)
        }

    @staticmethod
    def get(user:User, wikisection:wikisection.WikiSection, currentuser:User):
        try: 
            if not wikisection.permissionsable(currentuser):
                return None
            result = PermissionSection.objects.get(grantedto=user, section = wikisection)
            if not (result is None):
                return result
        except Exception:
            pass
        return PermissionSection(createdby=currentuser, grantedto=user, section=wikisection)

    @staticmethod
    def fromjson(jsonobj:dict, section:wikisection.WikiSection, commit:bool=False):
        try: 
            if section is None:
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
                return None
            if 'createdby' in jsonobj:
                try:
                    user = User.objects.get(username=jsonobj['createdby'])
                    crby = user
                except Exception:
                    pass
            result = PermissionSection.get(grto, section, crby)
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
