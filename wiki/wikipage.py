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
from dndhelper import sendemail as emailsending
from dndhelper.widget import quill
from permissions.permissions import PERMISSION_LEVELS_DICTIONARY, Permission


def time_now(instance=None):
    return datetime.now(pytz.utc)

class Keywords(models.Model):
    word = models.CharField('Word', max_length=120, null=False, blank=False)


class WikiPage(models.Model):
    unid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    createdon = models.DateTimeField("Created time", auto_now_add=True, null=False, blank=False)
    updatedon = models.DateTimeField("Updated time", auto_now_add=True, null=False, blank=False)
    createdby = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Created by", null=True, blank=True, related_name='createdwikiarticles')
    updatedby = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name="Updated by", null=True, blank=True, related_name='lastupdatedwikiarticles')
    commonknowledge = models.BooleanField("Is common knowledge?", default=False)
    title = models.CharField("Title*", max_length=160, null=False, blank=False)
    keywords = models.ManyToManyField("Keywords", verbose_name="Keywords")
    text = models.TextField("Article text", null=True, blank=True)

    def save(self, *args, **kwargs):
        folder = self.get_files_folder()
        if folder is not None:
            self.text = quill.save_images_from_quill(self.text, folder)
        super(WikiPage, self).save(*args, **kwargs)

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
    
    def __str__(self) -> str:
        return "Wiki title: " + str(self.title) + ". UNID: " + str(self.unid)

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
            folder_path = os.path.join(settings.WIKI_FILES, str(self.unid))
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            return folder_path
        except Exception:
            return None
       
    def generate_link(self) -> str:
        return self.get_link()
       
    def get_link(self) -> str:
        return reverse('wiki_page', kwargs={'wikipageuuid': self.unid})
       
    def get_files_link(self) -> str:
        return reverse('wiki_page_file_empty', kwargs={'wikipageuuid': self.unid})

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
        for section in self.wikisection_set.all():
            if section.viewable(user):
                return True
        return False

    def allviewable(self, user: User) -> list:
        if user is None:
            user = get_current_user()
        if user is None:
            return []
        allsections =  self.wikisection_set.all().order_by('pageorder')
        if user.is_superuser:
            return list(allsections)
        sect = []
        for section in allsections:
            if section.viewable(user):
                sect.append(section)
        return sect

    def alleditable(self, user: User) -> list:
        if user is None:
            user = get_current_user()
        if user is None:
            return []
        allsections =  self.wikisection_set.all().order_by('pageorder')
        if user.is_superuser:
            return list(allsections)
        sect = []
        for section in allsections:
            if section.editable(user):
                sect.append(section)
        return sect

    def allpermissionable(self, user: User) -> list:
        if user is None:
            user = get_current_user()
        if user is None:
            return []
        allsections =  self.wikisection_set.all().order_by('pageorder')
        if user.is_superuser:
            return list(allsections)
        sect = []
        for section in allsections:
            if section.permissionsable(user):
                sect.append(section)
        return sect

    def sections_list(self)->list:
        result = []
        for sec in self.wikisection_set.all():
            result.append(sec.json())
        return result

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
            'text': json.loads(self.text) if self.is_quill_content() else quill.quillify_text(self.text),
            'sec': self.sections_list(),
            'perm': self.permission_list()
        }

    
    @staticmethod
    def fromjson(jsonobject:dict, commit:bool = False, override:bool = False):
        result = WikiPage()
        if not ('title' in jsonobject):
            return None
        tmp = None
        if 'unid' in jsonobject:
            try:
                result.unid = uuid.UUID(jsonobject['unid'])
                try:
                    tmp = WikiPage.objects.get(unid = result.unid)
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
            sections = []
            if 'sec' in jsonobject:
                try:
                    from wiki.wikisection import WikiSection
                    for sec in jsonobject['sec']:
                        sections.append(WikiSection.fromjson(sec, result, commit=commit))
                except Exception:
                    pass 
            perms = []
            if 'perm' in jsonobject:
                try:
                    from wiki.permissionpage import PermissionPage
                    for perm in jsonobject['perm']:
                        perms.append(PermissionPage.fromjson(perm, result, commit=commit))
                except Exception:
                    pass 
            return {'page': result, 'sec':sections, 'perm': perms}
        except Exception as exc:
            print(exc)
            return None
        return None
    
    @staticmethod
    def cancreate(user):
        if user is None:
            user = get_current_user()
        if user is None:
            return False
        return user.is_superuser

    # def is_quill_content(self):
    #     return quill.check_quill_string(self.description)

    # def get_quill_content(self):
    #     return quill.get_quill_text(self.description)

    # def get_content(self):
    #     return self.description
