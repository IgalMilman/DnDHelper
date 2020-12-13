import json
import os
import uuid
from datetime import datetime, timedelta

import mock
import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from dndhelper.widget import quill
from permissions import permissions_response
from permissions.permissions import (PERMISSION_LEVELS_DICTIONARY,
                                     PERMISSION_LEVELS_TUPLES, Permission)
from wiki import modelgetters, wikipermissionsresponse
from wiki.permissionsection import PermissionSection
from wiki.wikipage import Keywords, WikiPage
from wiki.wikisection import WikiSection


class req:
    def __init__(self, method='GET', post={}, getdic={}, user=None):
        self.method = method
        self.user = user
        self.POST = post
        self.GET = getdic


class WikiPermissionsResponseTesting(TestCase):
    def setUp(self):
        self.permsecjson = PermissionSection.json
        self.permsecfromjson = PermissionSection.fromjson
        self.wikisecjson = WikiSection.json
        self.wikisecfromjson = WikiSection.fromjson
        self.wikisPermable = WikiSection.permissionsable 
        self.wikipageedit = WikiPage.editable
        self.firstUser = User(is_superuser=True, username='test1', password='test1', email='test1@example.com', first_name='testname1', last_name='testlast2')
        self.secondUser = User(is_superuser=False, username='test2', password='test2', email='test2@example.com', first_name='testname2', last_name='testlast2')
        self.thirdUser = User(is_superuser=False, username='test3', password='test3', email='test3@example.com', first_name='testname3', last_name='testlast3')
        self.fourthUser = User(is_superuser=False, username='test4', password='test4', email='test4@example.com', first_name='testname4', last_name='testlast4')        
        self.firstUser.save()
        self.secondUser.save()        
        self.thirdUser.save()
        self.fourthUser.save()
        self.usersList = [self.firstUser, self.secondUser, self.thirdUser, self.fourthUser]
        self.wikiuuid = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
        self.wikistext = ['{"ops":[{"insert":"123123\\n"}]}', 'text', None]
        self.wikisuuid = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
        self.createdtime = datetime.now(pytz.utc)
        self.wikiPages = []
        self.permissions = []
        self.permissionsSecondSec = []
        for i in range(2):
            self.wikiPages.append(WikiPage(unid=self.wikiuuid[i], createdon=self.createdtime, updatedon=self.createdtime, createdby=self.firstUser, updatedby=self.secondUser, title='testpage'+str(i+1)))
            self.wikiPages[i].save()
            self.wikiPages[i].createdon=self.createdtime + timedelta(hours=i)
            self.wikiPages[i].updatedon=self.createdtime + timedelta(hours=i)
            self.wikiPages[i].save()
        self.wikiSections = []
        for i in range(3):
            self.wikiSections.append(WikiSection(unid=self.wikisuuid[i], createdon=self.createdtime, updatedon=self.createdtime, createdby=self.firstUser, updatedby=self.secondUser, title='testsec'+str(i+1), pageorder=i+1, text=self.wikistext[i], wikipage=self.wikiPages[0]))
            self.wikiSections[i].save()
            self.wikiSections[i].createdon=self.createdtime + timedelta(hours=i)
            self.wikiSections[i].updatedon=self.createdtime + timedelta(hours=i)
            perm = PermissionSection(createdby=self.firstUser, accesslevel=10, grantedto=self.thirdUser, section=self.wikiSections[i])
            perm.save()
            if i==1:
                self.permissionsSecondSec.append(perm)
            self.permissions.append(perm)
            perm = PermissionSection(createdby=self.firstUser, accesslevel=30, grantedto=self.secondUser, section=self.wikiSections[i])
            if i==1:
                self.wikiSections[1].createdby = None
                self.wikiSections[1].updatedby = None
                perm.accesslevel = 10
                self.permissionsSecondSec.insert(0, perm)
            perm.save()
            self.permissions.append(perm)
            self.wikiSections[i].save()
        # wikisectionform.settings.SOFTWARE_NAME_SHORT = self.softwarename
        # os.path.exists = mock.Mock(return_value=True, spec='os.path.exists')
        # os.makedirs = mock.Mock(return_value=None, spec='os.makedirs')
        # wikisectionform.render = mock.Mock(side_effect=render_mock)
        # wikisectionform.redirect = mock.Mock(side_effect=redirect_mock)
        # wikisectionform.reverse = mock.Mock(side_effect=reverse_mock)
        # wikipage.reverse = mock.Mock(side_effect=reverse_mock)
        # wikisection.reverse = mock.Mock(side_effect=reverse_mock)  
    
    def tearDown(self):
        PermissionSection.json = self.permsecjson
        PermissionSection.fromjson = self.permsecfromjson
        WikiSection.json = self.wikisecjson
        WikiSection.fromjson = self.wikisecfromjson
        WikiSection.permissionsable = self.wikisPermable
        WikiPage.editable = self.wikipageedit

    def test_permission_section_json(self):
        permsecres = self.permissions[0].json()
        permsecres_right = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': self.permissions[0].createdby.get_username(),
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        self.assertDictEqual(permsecres, permsecres_right)

    def test_permission_section_no_created_json(self):
        self.permissions[0].createdby = None
        permsecres = self.permissions[0].json()
        permsecres_right = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': None,
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        self.assertDictEqual(permsecres, permsecres_right)

    def test_wiki_section_json_first(self):
        PermissionSection.json = mock.Mock(return_value={'permsec':'qwe'})
        wikisec = self.wikiSections[0].json()
        wikisec_right = {
            'unid': str(self.wikiSections[0].unid),
            'createdon': self.wikiSections[0].createdon.isoformat(),
            'createdby': self.wikiSections[0].createdby.get_username(),
            'updatedon': self.wikiSections[0].updatedon.isoformat(),
            'updatedby': self.wikiSections[0].updatedby.get_username(),
            'pageorder': self.wikiSections[0].pageorder,
            'title': self.wikiSections[0].title,
            'commonknowledge': False,
            'text': json.loads(self.wikiSections[0].text) if self.wikiSections[0].is_quill_content() else quill.quillify_text(self.wikiSections[0].text),
            'perm': [{'permsec':'qwe'}, {'permsec':'qwe'}] 
        }
        self.assertDictEqual(wikisec, wikisec_right)
        self.assertEqual(PermissionSection.json.call_count, len(self.wikiSections[0].permissions.all()))

    def test_wiki_section_json_second(self):
        PermissionSection.json = mock.Mock(return_value={'permsec':'qwe'})
        wikisec = self.wikiSections[1].json()
        wikisec_right = {
            'unid': str(self.wikiSections[1].unid),
            'createdon': self.wikiSections[1].createdon.isoformat(),
            'createdby': None,
            'updatedon': self.wikiSections[1].updatedon.isoformat(),
            'updatedby': None,
            'pageorder': self.wikiSections[1].pageorder,
            'title': self.wikiSections[1].title,
            'commonknowledge': False,
            'text': json.loads(self.wikiSections[1].text) if self.wikiSections[1].is_quill_content() else quill.quillify_text(self.wikiSections[1].text),
            'perm': [{'permsec':'qwe'}, {'permsec':'qwe'}] 
        }
        self.assertDictEqual(wikisec, wikisec_right)
        self.assertEqual(PermissionSection.json.call_count, len(self.wikiSections[1].permissions.all()))


    def test_wiki_page_json_first(self):
        WikiSection.json = mock.Mock(return_value={'sec':'qwe'})
        wikipage = self.wikiPages[0].json()
        wikipage_right = {
            'unid': str(self.wikiPages[0].unid),
            'createdon': self.wikiPages[0].createdon.isoformat(),
            'createdby': self.wikiPages[0].createdby.get_username(),
            'updatedon': self.wikiPages[0].updatedon.isoformat(),
            'updatedby': self.wikiPages[0].updatedby.get_username(),
            'commonknowledge': self.wikiPages[0].commonknowledge,
            'title': self.wikiPages[0].title,
            'commonknowledge': False,
            'text': json.loads(self.wikiPages[0].text) if self.wikiPages[0].is_quill_content() else quill.quillify_text(self.wikiPages[0].text),
            'sec': [{'sec':'qwe'}, {'sec':'qwe'}, {'sec':'qwe'}] 
        }
        self.assertDictEqual(wikipage, wikipage_right)
        self.assertEqual(WikiSection.json.call_count, len(self.wikiPages[0].wikisection_set.all()))
        
    def test_wiki_page_json_second(self):
        WikiSection.json = mock.Mock(return_value={'sec':'qwe'})
        wikipage = self.wikiPages[1].json()
        wikipage_right = {
            'unid': str(self.wikiPages[1].unid),
            'createdon': self.wikiPages[1].createdon.isoformat(),
            'createdby': self.wikiPages[1].createdby.get_username(),
            'updatedon': self.wikiPages[1].updatedon.isoformat(),
            'updatedby': self.wikiPages[1].updatedby.get_username(),
            'commonknowledge': self.wikiPages[1].commonknowledge,
            'title': self.wikiPages[1].title,
            'commonknowledge': False,
            'text': json.loads(self.wikiPages[1].text) if self.wikiPages[1].is_quill_content() else quill.quillify_text(self.wikiPages[1].text),
            'sec': [] 
        }
        self.assertDictEqual(wikipage, wikipage_right)
        self.assertEqual(WikiSection.json.call_count, len(self.wikiPages[1].wikisection_set.all()))

    def test_permission_section_from_json_fail_no_granted(self):
        permsec = {
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': self.permissions[0].createdby.get_username(),
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        section = self.permissions[0].section
        result = PermissionSection.fromjson(permsec, section, commit = False)
        self.assertIsNone(result)

    def test_permission_section_from_json_fail_wrong_granted(self):
        permsec = {
            'grantedto': 'qweryty',
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': self.permissions[0].createdby.get_username(),
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        section = self.permissions[0].section
        result = PermissionSection.fromjson(permsec, section, commit = False)
        self.assertIsNone(result)

    def test_permission_section_from_json_fail_no_perm_level(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': self.permissions[0].createdby.get_username(),
            'section': str(self.permissions[0].section.unid),
        }
        section = self.permissions[0].section
        result = PermissionSection.fromjson(permsec, section, commit = False)
        self.assertIsNone(result)

    def test_permission_section_from_json_fail_wrong_perm_level(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': self.permissions[0].createdby.get_username(),
            'permlevel': 'qwerty',
            'section': str(self.permissions[0].section.unid),
        }
        section = self.permissions[0].section
        result = PermissionSection.fromjson(permsec, section, commit = False)
        self.assertIsNone(result)

    def test_permission_section_from_json_fail_no_section(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': self.permissions[0].createdby.get_username(),
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        section = None
        result = PermissionSection.fromjson(permsec, section, commit = False)
        self.assertIsNone(result)

    def test_permission_section_from_json_fail_permissions(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': self.fourthUser,
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        section = self.permissions[0].section
        result = PermissionSection.fromjson(permsec, section, commit = False)
        self.assertIsNone(result)

    def test_permission_section_from_json_success_everything_no_commit(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': self.permissions[0].createdby.get_username(),
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        section = self.permissions[0].section
        PermissionSection.objects.all().delete()
        result = PermissionSection.fromjson(permsec, section, commit = False)
        self.assertEqual(len(PermissionSection.objects.all()), 0)
        self.assertEqual(result.grantedto, self.permissions[0].grantedto)
        self.assertEqual(result.createdby, self.permissions[0].createdby)
        self.assertEqual(result.accesslevel, self.permissions[0].accesslevel)
        self.assertEqual(result.section, self.permissions[0].section)
        self.assertNotEqual(result.id, self.permissions[0].id)

    def test_permission_section_from_json_success_everything_commit(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': self.permissions[0].createdby.get_username(),
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        section = self.permissions[0].section
        PermissionSection.objects.all().delete()
        result = PermissionSection.fromjson(permsec, section, commit = True)
        self.assertEqual(len(PermissionSection.objects.all()), 1)
        self.assertEqual(result.grantedto, self.permissions[0].grantedto)
        self.assertEqual(result.createdby, self.permissions[0].createdby)
        self.assertEqual(result.accesslevel, self.permissions[0].accesslevel)
        self.assertEqual(result.section, self.permissions[0].section)
        self.assertNotEqual(result.id, self.permissions[0].id)

    def test_permission_section_from_json_success_no_created_by(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        WikiSection.permissionsable = mock.Mock(return_value=True)
        section = self.permissions[0].section
        PermissionSection.objects.all().delete()
        result = PermissionSection.fromjson(permsec, section, commit = True)
        self.assertEqual(len(PermissionSection.objects.all()), 1)
        self.assertEqual(result.grantedto, self.permissions[0].grantedto)
        self.assertEqual(result.createdby, None)
        self.assertEqual(result.accesslevel, self.permissions[0].accesslevel)
        self.assertEqual(result.section, self.permissions[0].section)
        self.assertNotEqual(result.id, self.permissions[0].id)

    def test_permission_section_from_json_success_wrong_created_by(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': self.permissions[0].createdon.isoformat(),
            'createdby': 'qwerty',
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        WikiSection.permissionsable = mock.Mock(return_value=True)
        section = self.permissions[0].section
        PermissionSection.objects.all().delete()
        result = PermissionSection.fromjson(permsec, section, commit = True)
        self.assertEqual(len(PermissionSection.objects.all()), 1)
        self.assertEqual(result.grantedto, self.permissions[0].grantedto)
        self.assertEqual(result.createdby, None)
        self.assertEqual(result.accesslevel, self.permissions[0].accesslevel)
        self.assertEqual(result.section, self.permissions[0].section)
        self.assertNotEqual(result.id, self.permissions[0].id)

    def test_permission_section_from_json_success_no_date_commit(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdby': self.permissions[0].createdby.get_username(),
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        section = self.permissions[0].section
        PermissionSection.objects.all().delete()
        result = PermissionSection.fromjson(permsec, section, commit = True)
        self.assertEqual(len(PermissionSection.objects.all()), 1)
        self.assertEqual(result.grantedto, self.permissions[0].grantedto)
        self.assertEqual(result.createdby, self.permissions[0].createdby)
        self.assertEqual(result.accesslevel, self.permissions[0].accesslevel)
        self.assertEqual(result.section, self.permissions[0].section)
        self.assertNotEqual(result.id, self.permissions[0].id)

    def test_permission_section_from_json_success_wrong_date_commit(self):
        permsec = {
            'grantedto': self.permissions[0].grantedto.get_username(),
            'createdon': 'qwerty',
            'createdby': self.permissions[0].createdby.get_username(),
            'permlevel': self.permissions[0].accesslevel,
            'section': str(self.permissions[0].section.unid),
        }
        section = self.permissions[0].section
        PermissionSection.objects.all().delete()
        result = PermissionSection.fromjson(permsec, section, commit = True)
        self.assertEqual(len(PermissionSection.objects.all()), 1)
        self.assertEqual(result.grantedto, self.permissions[0].grantedto)
        self.assertEqual(result.createdby, self.permissions[0].createdby)
        self.assertEqual(result.accesslevel, self.permissions[0].accesslevel)
        self.assertEqual(result.section, self.permissions[0].section)
        self.assertNotEqual(result.id, self.permissions[0].id)
        
    def test_wiki_section_from_json_fail_no_page(self):
        secid = 0
        wikisec_right = {
            'unid': str(self.wikiSections[secid].unid),
            'createdon': self.wikiSections[secid].createdon.isoformat(),
            'createdby': self.wikiSections[secid].createdby.get_username(),
            'updatedon': self.wikiSections[secid].updatedon.isoformat(),
            'updatedby': self.wikiSections[secid].updatedby.get_username(),
            'pageorder': self.wikiSections[secid].pageorder,
            'title': self.wikiSections[secid].title,
            'text': json.loads(self.wikiSections[secid].text) if self.wikiSections[secid].is_quill_content() else quill.quillify_text(self.wikiSections[secid].text),
            'perm': [{'permsec':'qwe'}, {'permsec':'qwe'}] 
        }
        wikipage = None
        PermissionSection.fromjson = mock.Mock(return_value='result')
        WikiPage.editable = mock.Mock(return_value=True)
        resultdict = WikiSection.fromjson(wikisec_right, wikipage, commit = False)
        self.assertIsNone(resultdict)
        
    def test_wiki_section_from_json_fail_no_permissions(self):
        secid = 0
        wikisec_right = {
            'unid': str(self.wikiSections[secid].unid),
            'createdon': self.wikiSections[secid].createdon.isoformat(),
            'createdby': self.wikiSections[secid].createdby.get_username(),
            'updatedon': self.wikiSections[secid].updatedon.isoformat(),
            'updatedby': self.wikiSections[secid].updatedby.get_username(),
            'pageorder': self.wikiSections[secid].pageorder,
            'title': self.wikiSections[secid].title,
            'text': json.loads(self.wikiSections[secid].text) if self.wikiSections[secid].is_quill_content() else quill.quillify_text(self.wikiSections[secid].text),
            'perm': [{'permsec':'qwe'}, {'permsec':'qwe'}] 
        }
        wikipage = self.wikiPages[0]
        PermissionSection.fromjson = mock.Mock(return_value='result')
        WikiPage.editable = mock.Mock(return_value=False)
        resultdict = WikiSection.fromjson(wikisec_right, wikipage, commit = False)
        self.assertIsNone(resultdict)
        
    def test_wiki_section_from_json_fail_no_title(self):
        secid = 0
        wikisec_right = {
            'unid': str(self.wikiSections[secid].unid),
            'createdon': self.wikiSections[secid].createdon.isoformat(),
            'createdby': self.wikiSections[secid].createdby.get_username(),
            'updatedon': self.wikiSections[secid].updatedon.isoformat(),
            'updatedby': self.wikiSections[secid].updatedby.get_username(),
            'pageorder': self.wikiSections[secid].pageorder,
            'text': json.loads(self.wikiSections[secid].text) if self.wikiSections[secid].is_quill_content() else quill.quillify_text(self.wikiSections[secid].text),
            'perm': [{'permsec':'qwe'}, {'permsec':'qwe'}] 
        }
        wikipage = self.wikiPages[0]
        PermissionSection.fromjson = mock.Mock(return_value='result')
        WikiPage.editable = mock.Mock(return_value=True)
        resultdict = WikiSection.fromjson(wikisec_right, wikipage, commit = False)
        self.assertIsNone(resultdict)
        
    def test_wiki_section_from_json_fail_no_page_order(self):
        secid = 0
        wikisec_right = {
            'unid': str(self.wikiSections[secid].unid),
            'createdon': self.wikiSections[secid].createdon.isoformat(),
            'createdby': self.wikiSections[secid].createdby.get_username(),
            'updatedon': self.wikiSections[secid].updatedon.isoformat(),
            'updatedby': self.wikiSections[secid].updatedby.get_username(),
            'title': self.wikiSections[secid].title,
            'text': json.loads(self.wikiSections[secid].text) if self.wikiSections[secid].is_quill_content() else quill.quillify_text(self.wikiSections[secid].text),
            'perm': [{'permsec':'qwe'}, {'permsec':'qwe'}] 
        }
        wikipage = self.wikiPages[0]
        PermissionSection.fromjson = mock.Mock(return_value='result')
        WikiPage.editable = mock.Mock(return_value=True)
        resultdict = WikiSection.fromjson(wikisec_right, wikipage, commit = False)
        self.assertIsNone(resultdict)
        
    def test_wiki_section_from_json_fail_wrong_page_order(self):
        secid = 0
        wikisec_right = {
            'unid': str(self.wikiSections[secid].unid),
            'createdon': self.wikiSections[secid].createdon.isoformat(),
            'createdby': self.wikiSections[secid].createdby.get_username(),
            'updatedon': self.wikiSections[secid].updatedon.isoformat(),
            'updatedby': self.wikiSections[secid].updatedby.get_username(),
            'pageorder': 'qwerty',
            'title': self.wikiSections[secid].title,
            'text': json.loads(self.wikiSections[secid].text) if self.wikiSections[secid].is_quill_content() else quill.quillify_text(self.wikiSections[secid].text),
            'perm': [{'permsec':'qwe'}, {'permsec':'qwe'}] 
        }
        wikipage = self.wikiPages[0]
        PermissionSection.fromjson = mock.Mock(return_value='result')
        WikiPage.editable = mock.Mock(return_value=True)
        resultdict = WikiSection.fromjson(wikisec_right, wikipage, commit = False)
        self.assertIsNone(resultdict)
        
    def test_wiki_section_from_json_success_no_commit(self):
        secid = 0
        wikisec_right = {
            'unid': str(self.wikiSections[secid].unid),
            'createdon': self.wikiSections[secid].createdon.isoformat(),
            'createdby': self.wikiSections[secid].createdby.get_username(),
            'updatedon': self.wikiSections[secid].updatedon.isoformat(),
            'updatedby': self.wikiSections[secid].updatedby.get_username(),
            'pageorder': self.wikiSections[secid].pageorder,
            'title': self.wikiSections[secid].title,
            'text': json.loads(self.wikiSections[secid].text) if self.wikiSections[secid].is_quill_content() else quill.quillify_text(self.wikiSections[secid].text),
            'perm': [{'permsec':'qwe'}, {'permsec':'qwe'}] 
        }
        wikipage = self.wikiPages[0]
        WikiSection.objects.all().delete()
        PermissionSection.fromjson = mock.Mock(return_value='result')
        WikiPage.editable = mock.Mock(return_value=True)
        resultdict = WikiSection.fromjson(wikisec_right, wikipage, commit = False)
        result = resultdict['sec']
        self.assertEqual(len(WikiSection.objects.all()), 0)
        self.assertEqual(PermissionSection.fromjson.call_count, len(wikisec_right['perm']))
        self.assertEqual(result.unid, self.wikiSections[secid].unid)
        self.assertEqual(result.createdby, self.wikiSections[secid].createdby)
        self.assertEqual(result.updatedby, self.wikiSections[secid].updatedby)
        self.assertEqual(result.wikipage, self.wikiSections[secid].wikipage)
        self.assertEqual(result.pageorder, self.wikiSections[secid].pageorder)
        self.assertEqual(result.title, self.wikiSections[secid].title)
        self.assertNotEqual(result.id, self.wikiSections[secid].id)
        
    def test_wiki_section_from_json_success_commit(self):
        secid = 0
        wikisec_right = {
            'unid': str(self.wikiSections[secid].unid),
            'createdon': self.wikiSections[secid].createdon.isoformat(),
            'createdby': self.wikiSections[secid].createdby.get_username(),
            'updatedon': self.wikiSections[secid].updatedon.isoformat(),
            'updatedby': self.wikiSections[secid].updatedby.get_username(),
            'pageorder': self.wikiSections[secid].pageorder,
            'title': self.wikiSections[secid].title,
            'text': json.loads(self.wikiSections[secid].text) if self.wikiSections[secid].is_quill_content() else quill.quillify_text(self.wikiSections[secid].text),
            'perm': [{'permsec':'qwe'}, {'permsec':'qwe'}] 
        }
        wikipage = self.wikiPages[0]
        WikiSection.objects.all().delete()
        PermissionSection.fromjson = mock.Mock(return_value='result')
        WikiPage.editable = mock.Mock(return_value=True)
        resultdict = WikiSection.fromjson(wikisec_right, wikipage, commit = True)
        result = resultdict['sec']
        self.assertEqual(len(WikiSection.objects.all()), 1)
        self.assertEqual(PermissionSection.fromjson.call_count, len(wikisec_right['perm']))
        self.assertEqual(result.unid, self.wikiSections[secid].unid)
        self.assertEqual(result.createdby, self.wikiSections[secid].createdby)
        self.assertEqual(result.updatedby, self.wikiSections[secid].updatedby)
        self.assertEqual(result.wikipage, self.wikiSections[secid].wikipage)
        self.assertEqual(result.pageorder, self.wikiSections[secid].pageorder)
        self.assertEqual(result.title, self.wikiSections[secid].title)
        self.assertNotEqual(result.id, self.wikiSections[secid].id)
        

    def test_wiki_page_from_json_fail_no_title(self):
        pageid = 0
        wikip = self.wikiPages[pageid]
        wikipage_right = {
            'unid': str(wikip.unid),
            'createdon': wikip.createdon.isoformat(),
            'createdby': wikip.createdby.get_username(),
            'updatedon': wikip.updatedon.isoformat(),
            'updatedby': wikip.updatedby.get_username(),
            'commonknowledge': wikip.commonknowledge,
            'text': json.loads(wikip.text) if wikip.is_quill_content() else quill.quillify_text(wikip.text),
            'sec': [{'sec':'qwe'}, {'sec':'qwe'}, {'sec':'qwe'}] 
        }
        WikiSection.fromjson = mock.Mock(return_value='result')
        resultdict = WikiPage.fromjson(wikipage_right, commit=False)
        self.assertIsNone(resultdict)

    def test_wiki_page_from_json_success_no_commit(self):
        pageid = 0
        wikip = self.wikiPages[pageid]
        wikipage_right = {
            'unid': str(wikip.unid),
            'createdon': wikip.createdon.isoformat(),
            'createdby': wikip.createdby.get_username(),
            'updatedon': wikip.updatedon.isoformat(),
            'updatedby': wikip.updatedby.get_username(),
            'commonknowledge': wikip.commonknowledge,
            'title': wikip.title,
            'text': json.loads(wikip.text) if wikip.is_quill_content() else quill.quillify_text(wikip.text),
            'sec': [{'sec':'qwe'}, {'sec':'qwe'}, {'sec':'qwe'}] 
        }
        WikiSection.fromjson = mock.Mock(return_value='result')
        WikiPage.objects.all().delete()
        resultdict = WikiPage.fromjson(wikipage_right, commit=False)
        result = resultdict['page']
        self.assertEqual(len(WikiPage.objects.all()), 0)
        self.assertEqual(WikiSection.fromjson.call_count, len(wikipage_right['sec']))
        self.assertEqual(result.unid, wikip.unid)
        self.assertEqual(result.createdby, wikip.createdby)
        self.assertEqual(result.updatedby, wikip.updatedby)
        self.assertEqual(result.commonknowledge, wikip.commonknowledge)
        self.assertEqual(result.title, wikip.title)
        self.assertNotEqual(result.id, wikip.id)

    def test_wiki_page_from_json_success_commit(self):
        pageid = 0
        wikip = self.wikiPages[pageid]
        wikipage_right = {
            'unid': str(wikip.unid),
            'createdon': wikip.createdon.isoformat(),
            'createdby': wikip.createdby.get_username(),
            'updatedon': wikip.updatedon.isoformat(),
            'updatedby': wikip.updatedby.get_username(),
            'commonknowledge': wikip.commonknowledge,
            'title': wikip.title,
            'text': json.loads(wikip.text) if wikip.is_quill_content() else quill.quillify_text(wikip.text),
            'sec': [{'sec':'qwe'}, {'sec':'qwe'}, {'sec':'qwe'}] 
        }
        WikiSection.fromjson = mock.Mock(return_value='result')
        WikiPage.objects.all().delete()
        resultdict = WikiPage.fromjson(wikipage_right, commit=True)
        result = resultdict['page']
        self.assertEqual(len(WikiPage.objects.all()), 1)
        self.assertEqual(WikiSection.fromjson.call_count, len(wikipage_right['sec']))
        self.assertEqual(result.unid, wikip.unid)
        self.assertEqual(result.createdby, wikip.createdby)
        self.assertEqual(result.updatedby, wikip.updatedby)
        self.assertEqual(result.commonknowledge, wikip.commonknowledge)
        self.assertEqual(result.title, wikip.title)
        self.assertNotEqual(result.id, wikip.id)
        
#TODO add test for override

    def test_json_import_integration(self):
        WikiPage.editable = mock.Mock(return_value=True)
        WikiSection.permissionsable = mock.Mock(return_value=True)

        wikip = self.wikiPages[0]
        wikipagedictionary = self.wikiPages[0].json()
        wikipagejson = json.dumps(wikipagedictionary)
        WikiPage.objects.all().delete()
        wikipagerestoreddictionary = json.loads(wikipagejson)
        wikipage = WikiPage.fromjson(wikipagerestoreddictionary, commit=True)
        self.assertEqual(len(WikiPage.objects.all()), 1)
        self.assertEqual(len(WikiSection.objects.all()), 3)
        self.assertEqual(len(PermissionSection.objects.all()), 6)
