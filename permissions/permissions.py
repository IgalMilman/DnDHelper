from django.db import models
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.urls import reverse
import pytz, uuid, os
from urllib.parse import quote, unquote
from django.core.files.storage import DefaultStorage
from django.contrib.auth.models import User

def time_now(instance=None):
    return datetime.now(pytz.utc)

PERMISSION_LEVELS_DICTIONARY = {"Denied":0, "View Only":10, "View":10, "Permissions": 20, "Change Permissions": 20, "Edit": 30}
PERMISSION_LEVELS_TUPLES = ((0, "Denied"), (10, "View Only"), (20, "Change Permissions"), (30, "Edit"))

class Permission(models.Model):
    createdon = models.DateTimeField("Created time", auto_now_add=True, null=False, blank=False)
    createdby = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Created by", null=True, blank=True, related_name='createdpermissions')
    accesslevel = models.IntegerField("Access Level*", choices=PERMISSION_LEVELS_TUPLES, null=False, blank=False)
    grantedto = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Granted to", null=False, blank=False, related_name='apppermissions')
