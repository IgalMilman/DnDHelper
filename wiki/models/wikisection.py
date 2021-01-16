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
from wiki.models.wikipage import WikiPage


class WikiSection(models.Model):
    unid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    createdon = models.DateTimeField("Created time", auto_now_add=True, null=False, blank=False)
    updatedon = models.DateTimeField("Updated time", auto_now_add=True, null=False, blank=False)
    createdby = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Created by", null=True, blank=True, related_name='createdwikisections')
    updatedby = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Updated by", null=True, blank=True, related_name='lastupdatedwikisections')
    wikipage = models.ForeignKey(WikiPage, on_delete=models.CASCADE, null=False, blank=False)
    commonknowledge = models.BooleanField("Is common knowledge?", default=False)
    pageorder = models.IntegerField("Order*", null=False, blank=False)
    title = models.CharField("Title*", max_length=160, null=False, blank=False)
    text = models.TextField("Description of the issue", null=True, blank=True)

    def save(self, *args, **kwargs):
        folder = self.get_files_folder()
        if folder is not None:
            self.text = quill.save_images_from_quill(self.text, folder, self.get_files_link())
        super(WikiSection, self).save(*args, **kwargs)

    def createtime(self):
        return self.createdon.astimezone(pytz.timezone('America/New_York'))

    def updatetime(self):
        return self.updatedon.astimezone(pytz.timezone('America/New_York'))

    def createuser(self):
        if (self.createdby is None):
            return None
        return self.createdby.get_full_name()

    def updateuser(self):
        if (self.updatedby is None):
            return None
        return self.updatedby.get_full_name()
    
    def __str__(self):
        return "Wiki section: " + str(self.title) + ". UNID: " + str(self.unid)

    def editable(self, user=None):
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

    def permissionsable(self, user=None):
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

    def viewable(self, user=None):
        if user is None:
            user = get_current_user()
        if user is None:
            return False
        if user.is_superuser:
            return True
        try:
            if self.commonknowledge:
                return True
            permissionlevel = self.permissions.get(grantedto=user)
            if permissionlevel is None:
                return False
            return permissionlevel.accesslevel >= PERMISSION_LEVELS_DICTIONARY['View Only']
        except Exception:
            return False

       
    def generate_link(self):
        return self.get_link()
       
    def get_link(self):
        if (self.wikipage is None):
            return None
        return reverse('wiki_page', kwargs={'wikipageuuid': self.wikipage.unid})
       
    def get_files_link(self):
        if (self.wikipage is None):
            return None
        return reverse('wiki_section_file_empty', kwargs={'wikipageuuid': self.wikipage.unid, 'wikisectionuuid': self.unid})

    def get_files_folder(self):
        try:
            folder_path = os.path.join(settings.WIKI_SECTION_FILES, str(self.unid))
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            return folder_path
        except Exception:
            return None

    def get_file(self, filename):
        if os.path.exists(os.path.join(self.get_files_folder(), filename)):
            file = open(os.path.join(self.get_files_folder(), filename), 'rb')
            res = file.read()
            file.close()
            return res
        return None

    def is_quill_content(self):
        if self.text is None:
            return False
        return quill.check_quill_string(self.text)

    def get_quill_content(self):
        if self.text is None:
            return ''
        return quill.get_quill_text(self.text, files_link=self.get_files_link())

    def get_quill_content_simple(self):
        if self.text is None:
            return ''
        return quill.get_quill_text_simple(self.text, number_of_lines=number_of_lines)

    def get_content(self):
        return self.text

    def anchor_id(self):
        return 'a'+str(self.unid)

    def permission_list(self) -> list:
        result = []
        for perm in self.permissions.all():
            result.append(perm.json())
        return result

    def json(self)->dict:
        result = {
        'unid': str(self.unid),
        'createdon': self.createdon.isoformat(),
        'createdby': self.createdby.get_username() if self.createdby is not None else None,
        'updatedon': self.updatedon.isoformat(),
        'updatedby': self.updatedby.get_username() if self.updatedby is not None else None,
        'pageorder': self.pageorder,
        'commonknowledge': self.commonknowledge,
        'title': self.title,
        'text': quill.load_images_from_quill(json.loads(self.text) if self.is_quill_content() else quill.quillify_text(self.text), self.get_files_folder()),
        'perm': self.permission_list() 
        }
        return result

    @staticmethod
    def fromjson(jsonobject:dict, wikipage:WikiPage, commit:bool = False):
        if wikipage is None:
            return None
        if not wikipage.editable():
            return None
        if not ('title' in jsonobject):
            return None
        if not ('pageorder' in jsonobject):
            return None 
        pageord = None
        try:
            pageord = int(jsonobject['pageorder'])
        except Exception:
            return None
        result = WikiSection()
        result.wikipage = wikipage
        if 'unid' in jsonobject:
            try:
                result.unid = uuid.UUID(jsonobject['unid'])
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
        if 'pageorder' in jsonobject:
            try:
                result.pageorder = pageord
            except Exception:
                pass
        if 'title' in jsonobject:
            try:
                result.title = str(jsonobject['title'])
            except Exception:
                pass
        if 'commonknowledge' in jsonobject:
            try:
                result.commonknowledge = bool(jsonobject['commonknowledge'])
            except Exception:
                pass
        if 'text' in jsonobject:
            try:
                result.text = json.dumps(jsonobject['text'])
            except Exception:
                pass
        try:
            if commit:
                result.save()
            perms = []
            if 'perm' in jsonobject:
                try:
                    from wiki.models.permissionsection import PermissionSection
                    for perm in jsonobject['perm']:
                        perms.append(PermissionSection.fromjson(perm, result, commit=commit))
                except Exception:
                    pass 
            return {'sec': result, 'perm':perms}
        except Exception as exc:
            return None
        return None

