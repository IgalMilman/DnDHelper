import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, unquote

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import DefaultStorage
from django.db import models
from django.urls import reverse
from utils.usefull_functions import time_now

PERMISSION_LEVELS_DICTIONARY = {"Denied":0, "View Only":10, "View":10, "Permissions": 20, "Change Permissions": 20, "Edit": 30}
PERMISSION_LEVELS_TUPLES = ((0, "Denied"), (10, "View Only"), (20, "Change Permissions"), (30, "Edit"))

class Permission(models.Model):
    createdon = models.DateTimeField("Created time", auto_now_add=True, null=False, blank=False)
    createdby = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Created by", null=True, blank=True, related_name='createdpermissions')
    accesslevel = models.IntegerField("Access Level*", choices=PERMISSION_LEVELS_TUPLES, null=False, blank=False)
    grantedto = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Granted to", null=False, blank=False, related_name='apppermissions')
