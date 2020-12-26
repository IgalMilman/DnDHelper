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
from wiki.wikipage import WikiPage


class CEvent(WikiPage):
    eventday = models.IntegerField(verbose_name='Event Day')
    eventmonth = models.IntegerField(verbose_name='Event Month')
    eventyear = models.IntegerField(verbose_name='Event Year')