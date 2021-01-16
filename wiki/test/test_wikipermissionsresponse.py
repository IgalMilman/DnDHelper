import os
import uuid
from datetime import datetime, timedelta

import mock
import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from permissions import permissions_response
from permissions.models.permissions import (PERMISSION_LEVELS_DICTIONARY,
                                            PERMISSION_LEVELS_TUPLES,
                                            Permission)
from utils.widget import quill
from wiki import modelgetters, wikipermissionsresponse
from wiki.models import wikipage, wikisection
from wiki.models.permissionsection import PermissionSection
from wiki.models.wikipage import Keywords, WikiPage
from wiki.models.wikisection import WikiSection


class req:
    def __init__(self, method='GET', post={}, getdic={}, user=None):
        self.method = method
        self.user = user
        self.POST = post
        self.GET = getdic


class WikiPermissionsResponseTesting(TestCase):
    def setUp(self):
        self.setpermreq = wikipermissionsresponse.set_permissions_request_section
        self.setperm = wikipermissionsresponse.set_permissions_section
        self.getsec = wikipermissionsresponse.get_sections
        self.getusers = wikipermissionsresponse.get_users
        self.getpermdata = wikipermissionsresponse.get_permissions_data_section
        self.wikiperm = wikipermissionsresponse.get_permissions_for_section
        self.getperm = wikipermissionsresponse.permissions_response.get_permission_level_data
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
        self.wikipath = 'wiki'
        self.wikipagelink = 'wiki_page'
        self.wikimainpagelink = 'wiki_homepage'
        self.softwarename = 'name'
        self.formtemplate = 'forms/unimodelform.html'
        self.contenttype = 'text/html'
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
        settings.SOFTWARE_NAME_SHORT = self.softwarename 

    def tearDown(self):
        wikipermissionsresponse.get_permissions_for_section = self.wikiperm
        wikipermissionsresponse.permissions_response.get_permission_level_data = self.getperm
        wikipermissionsresponse.set_permissions_request_section = self.setpermreq
        wikipermissionsresponse.set_permissions_section = self.setperm
        wikipermissionsresponse.get_sections = self.getsec
        wikipermissionsresponse.get_permissions_data_section = self.getpermdata
        wikipermissionsresponse.get_users = self.getusers

    def test_get_all_users_data(self):
        users = wikipermissionsresponse.get_all_users_data()
        self.assertEqual(len(users), len(self.usersList))
        for i in range(len(self.usersList)):
            self.assertIsNone(users[i]['createdon'])
            self.assertIsNone(users[i]['createdby'])
            self.assertEqual(users[i]['grantedto']['username'], self.usersList[i].get_username())
            self.assertEqual(users[i]['grantedto']['fullname'], self.usersList[i].get_full_name())
            self.assertEqual(users[i]['grantedto']['issup'], self.usersList[i].is_superuser)
            self.assertEqual(users[i]['permlevel'], PERMISSION_LEVELS_TUPLES[0][0])

    def test_get_sections_all_success_super_user(self):
        request = req('GET', None, {'target': 'all'}, self.firstUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertListEqual(sections, self.wikiSections)

    def test_get_sections_all_success_permissions(self):
        request = req('GET', None, {'target': 'all'}, self.secondUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        del(self.wikiSections[1])
        self.assertListEqual(sections, self.wikiSections)

    def test_get_sections_one_success_super_user(self):
        request = req('GET', None, {'target': str(self.wikiSections[0].unid)}, self.firstUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertListEqual(sections, [self.wikiSections[0]])

    def test_get_sections_one_success_permissions(self):
        request = req('GET', None, {'target': str(self.wikiSections[0].unid)}, self.secondUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertListEqual(sections, [self.wikiSections[0]])

    def test_get_sections_all_failed_permissions(self):
        request = req('GET', None, {'target': 'all'}, self.thirdUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertListEqual(sections, [])

    def test_get_sections_one_failed_permissions(self):
        request = req('GET', None, {'target': str(self.wikiSections[0].unid)}, self.thirdUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertIsNone(sections)

    def test_get_sections_one_failed_no_target(self):
        request = req('GET', None, {'target': uuid.uuid4()}, self.firstUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertIsNone(sections)

    def test_get_sections_one_failed_no_page(self):
        request = req('GET', None, {'target': 'all'}, self.firstUser)
        sections = wikipermissionsresponse.get_sections(request, None)
        self.assertIsNone(sections)

    def test_post_sections_all_success_super_user(self):
        request = req('POST', {'targetid': 'all'}, None, self.firstUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertListEqual(sections, self.wikiSections)

    def test_post_sections_all_success_permissions(self):
        request = req('POST', {'targetid': 'all'}, None, self.secondUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        del(self.wikiSections[1])
        self.assertListEqual(sections, self.wikiSections)

    def test_post_sections_one_success_super_user(self):
        request = req('POST', {'targetid': str(self.wikiSections[0].unid)}, None, self.firstUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertListEqual(sections, [self.wikiSections[0]])

    def test_post_sections_one_success_permissions(self):
        request = req('POST', {'targetid': str(self.wikiSections[0].unid)}, None, self.secondUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertListEqual(sections, [self.wikiSections[0]])

    def test_post_sections_all_failed_permissions(self):
        request = req('POST', {'targetid': 'all'}, None, self.thirdUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertListEqual(sections, [])

    def test_post_sections_one_failed_permissions(self):
        request = req('POST', {'targetid': str(self.wikiSections[0].unid)}, None, self.thirdUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertIsNone(sections)

    def test_post_sections_one_failed_no_target(self):
        request = req('POST', {'targetid': uuid.uuid4()}, None, self.firstUser)
        sections = wikipermissionsresponse.get_sections(request, self.wikiPages[0])
        self.assertIsNone(sections)

    def test_post_sections_one_failed_no_page(self):
        request = req('POST', {'targetid': 'all'}, None, self.firstUser)
        sections = wikipermissionsresponse.get_sections(request, None)
        self.assertIsNone(sections)

    def test_get_permissions_for_section_success_sec_1_all_users(self):
        section = self.wikiSections[1]
        self.permissionsSecondSec.insert(0, permissions_response.get_permission_data_empty(self.firstUser))
        self.permissionsSecondSec.insert(0, permissions_response.get_permission_data_empty(User(username='all', first_name='All')))
        self.permissionsSecondSec.append(permissions_response.get_permission_data_empty(self.fourthUser))
        allusers = wikipermissionsresponse.get_all_users_data()
        permissions = wikipermissionsresponse.get_permissions_for_section(section, allusers)
        for i in [2, 3]:
            self.assertEqual(permissions[i]['createdon'], self.permissionsSecondSec[i].createdon)
            self.assertEqual(permissions[i]['createdby']['username'], self.permissionsSecondSec[i].createdby.get_username())
            self.assertEqual(permissions[i]['createdby']['fullname'], self.permissionsSecondSec[i].createdby.get_full_name())
            self.assertEqual(permissions[i]['createdby']['issup'], self.permissionsSecondSec[i].createdby.is_superuser)
            self.assertEqual(permissions[i]['grantedto']['username'], self.permissionsSecondSec[i].grantedto.get_username())
            self.assertEqual(permissions[i]['grantedto']['fullname'], self.permissionsSecondSec[i].grantedto.get_full_name())
            self.assertEqual(permissions[i]['grantedto']['issup'], self.permissionsSecondSec[i].grantedto.is_superuser)
            self.assertEqual(permissions[i]['permlevel'], self.permissionsSecondSec[i].accesslevel)
        for i in [0, 1, 4]:
            self.assertIsNone(permissions[i]['createdon'])
            self.assertIsNone(permissions[i]['createdby'])
            self.assertEqual(permissions[i]['grantedto']['username'], self.permissionsSecondSec[i]['grantedto']['username'])
            self.assertEqual(permissions[i]['grantedto']['fullname'], self.permissionsSecondSec[i]['grantedto']['fullname'])
            self.assertEqual(permissions[i]['grantedto']['issup'], self.permissionsSecondSec[i]['grantedto']['issup'])
            self.assertEqual(permissions[i]['permlevel'], PERMISSION_LEVELS_TUPLES[0][0])

    def test_get_permissions_for_section_success_sec_1_all_users_none(self):
        section = self.wikiSections[1]
        self.permissionsSecondSec.insert(0, permissions_response.get_permission_data_empty(self.firstUser))
        self.permissionsSecondSec.insert(0, permissions_response.get_permission_data_empty(User(username='all', first_name='All')))
        self.permissionsSecondSec.append(permissions_response.get_permission_data_empty(self.fourthUser))
        allusers = None
        permissions = wikipermissionsresponse.get_permissions_for_section(section, allusers)
        for i in [2, 3]:
            self.assertEqual(permissions[i]['createdon'], self.permissionsSecondSec[i].createdon)
            self.assertEqual(permissions[i]['createdby']['username'], self.permissionsSecondSec[i].createdby.get_username())
            self.assertEqual(permissions[i]['createdby']['fullname'], self.permissionsSecondSec[i].createdby.get_full_name())
            self.assertEqual(permissions[i]['createdby']['issup'], self.permissionsSecondSec[i].createdby.is_superuser)
            self.assertEqual(permissions[i]['grantedto']['username'], self.permissionsSecondSec[i].grantedto.get_username())
            self.assertEqual(permissions[i]['grantedto']['fullname'], self.permissionsSecondSec[i].grantedto.get_full_name())
            self.assertEqual(permissions[i]['grantedto']['issup'], self.permissionsSecondSec[i].grantedto.is_superuser)
            self.assertEqual(permissions[i]['permlevel'], self.permissionsSecondSec[i].accesslevel)
        for i in [0, 1, 4]:
            self.assertIsNone(permissions[i]['createdon'])
            self.assertIsNone(permissions[i]['createdby'])
            self.assertEqual(permissions[i]['grantedto']['username'], self.permissionsSecondSec[i]['grantedto']['username'])
            self.assertEqual(permissions[i]['grantedto']['fullname'], self.permissionsSecondSec[i]['grantedto']['fullname'])
            self.assertEqual(permissions[i]['grantedto']['issup'], self.permissionsSecondSec[i]['grantedto']['issup'])
            self.assertEqual(permissions[i]['permlevel'], PERMISSION_LEVELS_TUPLES[0][0])

    def test_get_permissions_for_section_success_sec_1_empty_all_users_none(self):
        section = self.wikiSections[1]
        allusers = None
        neededresult = [permissions_response.get_permission_data_empty(User(username='all', first_name='All'))]
        neededresult = neededresult + wikipermissionsresponse.get_all_users_data()
        PermissionSection.objects.all().delete()
        permissions = wikipermissionsresponse.get_permissions_for_section(section, allusers)
        for i in range(5):
            self.assertIsNone(permissions[i]['createdon'])
            self.assertIsNone(permissions[i]['createdby'])
            self.assertEqual(permissions[i]['grantedto']['username'], neededresult[i]['grantedto']['username'])
            self.assertEqual(permissions[i]['grantedto']['fullname'], neededresult[i]['grantedto']['fullname'])
            self.assertEqual(permissions[i]['grantedto']['issup'], neededresult[i]['grantedto']['issup'])
            self.assertEqual(permissions[i]['permlevel'], PERMISSION_LEVELS_TUPLES[0][0])

    def test_get_permissions_for_section_success_sec_1_empty_all_users(self):
        section = self.wikiSections[1]
        allusers = wikipermissionsresponse.get_all_users_data()
        neededresult = [permissions_response.get_permission_data_empty(User(username='all', first_name='All'))]
        neededresult = neededresult + wikipermissionsresponse.get_all_users_data()
        PermissionSection.objects.all().delete()
        permissions = wikipermissionsresponse.get_permissions_for_section(section, allusers)
        for i in range(5):
            self.assertIsNone(permissions[i]['createdon'])
            self.assertIsNone(permissions[i]['createdby'])
            self.assertEqual(permissions[i]['grantedto']['username'], neededresult[i]['grantedto']['username'])
            self.assertEqual(permissions[i]['grantedto']['fullname'], neededresult[i]['grantedto']['fullname'])
            self.assertEqual(permissions[i]['grantedto']['issup'], neededresult[i]['grantedto']['issup'])
            self.assertEqual(permissions[i]['permlevel'], PERMISSION_LEVELS_TUPLES[0][0])

    def test_get_users_all(self):
        request = req('POST', {'username': 'all'}, None, self.firstUser)
        users = wikipermissionsresponse.get_users(request)
        self.assertListEqual(users, list(User.objects.all()))

    def test_get_users_get_request(self):
        request = req('GET', None, {'username': 'all'}, self.firstUser)
        users = wikipermissionsresponse.get_users(request)
        self.assertIsNone(users)

    def test_get_users_success(self):
        request = req('POST', {'username': self.firstUser.get_username()}, None, self.firstUser)
        users = wikipermissionsresponse.get_users(request)
        self.assertListEqual(users, [self.firstUser])

    def test_get_users_fail(self):
        request = req('POST', {'username': 'something'}, None, self.firstUser)
        users = wikipermissionsresponse.get_users(request)
        self.assertIsNone(users)

    def test_get_wiki_page_success(self):
        request = req('POST', {'username': self.firstUser.get_username()}, None, self.firstUser)
        wikipage = wikipermissionsresponse.get_wiki_page(request, self.wikiPages[0].unid)
        self.assertEqual(wikipage, self.wikiPages[0])

    def test_get_wiki_page_fail(self):
        request = req('POST', {'username': self.firstUser.get_username()}, None, self.firstUser)
        wikipage = wikipermissionsresponse.get_wiki_page(request, uuid.uuid4())
        self.assertIsNone(wikipage)

    def test_set_permissions_users_none(self):
        result = wikipermissionsresponse.set_permissions_section(None, self.wikiSections[0], 10, self.firstUser)
        self.assertEqual(result, -1)

    def test_set_permissions_section_none(self):
        result = wikipermissionsresponse.set_permissions_section([self.firstUser], None, 10, self.firstUser)
        self.assertEqual(result, -1)

    def test_set_permissions_curuser_none(self):
        result = wikipermissionsresponse.set_permissions_section([self.firstUser], self.wikiSections[0], 10, None)
        self.assertEqual(result, -1)

    def test_set_permissions_curuser_no_permissions(self):
        result = wikipermissionsresponse.set_permissions_section([self.firstUser], self.wikiSections[0], 10, self.fourthUser)
        self.assertEqual(result, -1)

    def test_set_permissions_new_permission(self):
        count = len(PermissionSection.objects.all())
        result = wikipermissionsresponse.set_permissions_section([self.firstUser], self.wikiSections[0], 10, self.firstUser)
        self.assertEqual(result, 1)
        self.assertEqual(len(PermissionSection.objects.all()), count + 1)

    def test_set_permissions_change_permission(self):
        count = len(PermissionSection.objects.all())
        result = wikipermissionsresponse.set_permissions_section([self.secondUser], self.wikiSections[1], 20, self.firstUser)
        p = PermissionSection.objects.get(grantedto = self.secondUser, section = self.wikiSections[1])
        self.assertEqual(result, 1)
        self.assertEqual(len(PermissionSection.objects.all()), count)
        self.assertEqual(p.accesslevel, 20)

    def test_set_permissions_list_of_users(self):
        count = len(PermissionSection.objects.all())
        result = wikipermissionsresponse.set_permissions_section([self.firstUser, self.secondUser, self.fourthUser], self.wikiSections[1], 20, self.firstUser)
        self.assertEqual(result, 3)
        p = PermissionSection.objects.get(grantedto = self.firstUser, section = self.wikiSections[1])
        self.assertEqual(p.createdby, self.firstUser)
        self.assertEqual(p.accesslevel, 20)
        p = PermissionSection.objects.get(grantedto = self.secondUser, section = self.wikiSections[1])
        self.assertEqual(p.accesslevel, 20)
        p = PermissionSection.objects.get(grantedto = self.fourthUser, section = self.wikiSections[1])
        self.assertEqual(p.createdby, self.firstUser)
        self.assertEqual(p.accesslevel, 20)
        self.assertEqual(len(PermissionSection.objects.all()), count + 2)

    def test_get_permissions_data_none(self):
        sections = None
        self.assertIsNone(wikipermissionsresponse.get_permissions_data_section(sections))

    def test_get_permissions_data_one_section(self):
        sections = [self.wikiSections[0]]
        wikiperm = wikipermissionsresponse.get_permissions_for_section
        getperm = wikipermissionsresponse.permissions_response.get_permission_level_data
        wikipermissionsresponse.get_permissions_for_section = mock.Mock(return_value='permsec')
        wikipermissionsresponse.permissions_response.get_permission_level_data = mock.Mock(return_value='permlevel')
        result = wikipermissionsresponse.get_permissions_data_section(sections)
        self.assertEqual(wikipermissionsresponse.get_permissions_for_section.call_count, 1)
        self.assertEqual(wikipermissionsresponse.permissions_response.get_permission_level_data.call_count, 1)

        self.assertEqual(len(result['sections']), 1)
        self.assertEqual(result['permlevels'], 'permlevel')
        self.assertEqual(result['sections'][0]['secid'], self.wikiSections[0].unid)
        self.assertEqual(result['sections'][0]['sectitle'], self.wikiSections[0].title)
        self.assertEqual(result['sections'][0]['secperm'], 'permsec')
        

    def test_get_permissions_data_two_sections(self):
        sections = [self.wikiSections[0], self.wikiSections[1]]
        wikipermissionsresponse.get_permissions_for_section = mock.Mock(return_value='permsec')
        wikipermissionsresponse.permissions_response.get_permission_level_data = mock.Mock(return_value='permlevel')
        result = wikipermissionsresponse.get_permissions_data_section(sections)
        neededresult = [{'secid':None, 'sectitle':'All', 'secperm':'permsec'},
        {'secid':sections[0].unid, 'sectitle':sections[0].title, 'secperm':'permsec'},
        {'secid':sections[1].unid, 'sectitle':sections[1].title, 'secperm':'permsec'}]

        self.assertEqual(result['permlevels'], 'permlevel')
        self.assertEqual(wikipermissionsresponse.get_permissions_for_section.call_count, 3)
        self.assertEqual(permissions_response.get_permission_level_data.call_count, 1)
        self.assertEqual(len(result['sections']), 3)
        self.assertListEqual(result['sections'], neededresult)
        
    def test_set_permissions_request_no_permissionlevel(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser, self.secondUser])
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=2)
        sections = [self.wikiSections[0], self.wikiSections[1]]
        request = req('POST', {}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertIsNone(result)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 0)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, 0)
        
        
    def test_set_permissions_request_permissionlevel_not_number(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser, self.secondUser])
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=2)
        sections = [self.wikiSections[0], self.wikiSections[1]]
        request = req('POST', {'permissionlevel': 'q'}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertIsNone(result)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 0)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, 0)
        
        
    def test_set_permissions_request_sections_none(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser, self.secondUser])
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=2)
        sections = None
        request = req('POST', {'permissionlevel': 10}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertIsNone(result)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 0)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, 0)
        
        
    def test_set_permissions_request_get_users_none(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=None)
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=2)
        sections = [self.wikiSections[0], self.wikiSections[1]]
        request = req('POST', {'permissionlevel': 10}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertIsNone(result)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 1)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, 0)
        
    def test_set_permissions_request_get_users_error(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser], side_effect=Exception('Error'))
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=2)
        sections = [self.wikiSections[0], self.wikiSections[1]]
        request = req('POST', {'permissionlevel': 10}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertIsNone(result)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 1)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, 0)
        
    def test_set_permissions_request_set_perm_error(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser])
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=2, side_effect=Exception('Error'))
        sections = [self.wikiSections[0], self.wikiSections[1]]
        request = req('POST', {'permissionlevel': 10}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertIsNone(result)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 1)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, 1)
        
        
    def test_set_permissions_request_one_section(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser, self.secondUser])
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=2)
        sections = [self.wikiSections[0]]
        request = req('POST', {'permissionlevel': 10}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 1)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, len(sections))
        self.assertDictEqual(result, {'status': 'success', 'countcreated': len(sections)*len(wikipermissionsresponse.get_users()), 
        'countneeded':len(sections)*len(wikipermissionsresponse.get_users()) })
        
        
    def test_set_permissions_request_one_user(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser])
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=1)
        sections = [self.wikiSections[0], self.wikiSections[1]]
        request = req('POST', {'permissionlevel': 10}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 1)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, len(sections))
        self.assertDictEqual(result, {'status': 'success', 'countcreated': len(sections)*len(wikipermissionsresponse.get_users()), 
        'countneeded':len(sections)*len(wikipermissionsresponse.get_users()) })
        
        
    def test_set_permissions_request_one_user_one_section(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser])
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=1)
        sections = [self.wikiSections[0]]
        request = req('POST', {'permissionlevel': 10}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 1)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, len(sections))
        self.assertDictEqual(result, {'status': 'success', 'countcreated': len(sections)*len(wikipermissionsresponse.get_users()), 
        'countneeded':len(sections)*len(wikipermissionsresponse.get_users()) })
        
        
    def test_set_permissions_request_multiple_sections_multiple_users(self):
        wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser, self.secondUser])
        wikipermissionsresponse.set_permissions_section = mock.Mock(return_value=2)
        sections = [self.wikiSections[0], self.wikiSections[1]]
        request = req('POST', {'permissionlevel': 10}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertEqual(wikipermissionsresponse.get_users.call_count, 1)
        self.assertEqual(wikipermissionsresponse.set_permissions_section.call_count, len(sections))
        self.assertDictEqual(result, {'status': 'success', 'countcreated': len(sections)*len(wikipermissionsresponse.get_users()), 
        'countneeded':len(sections)*len(wikipermissionsresponse.get_users()) })
        
        
    def test_set_permissions_request_permissionlevel_real(self):
        #wikipermissionsresponse.get_users = mock.Mock(return_value=[self.firstUser, self.secondUser])
        #wikipermissionsresponse.set_permissions = mock.Mock(return_value=2)
        numperm = len(PermissionSection.objects.all())
        sections = [self.wikiSections[0], self.wikiSections[1]]
        request = req('POST', {'permissionlevel': 10, 'username': self.firstUser.get_username()}, None, self.firstUser)
        result = wikipermissionsresponse.set_permissions_request_section(request, sections)
        self.assertEqual(len(PermissionSection.objects.all()), numperm + 2)
        self.assertDictEqual(result, {'status': 'success', 'countcreated': len(sections), 
        'countneeded':len(sections) })
        
    def test_handle_permissions_request_sections_is_none(self):
        wikipermissionsresponse.get_sections = mock.Mock(return_value=None)
        wikipermissionsresponse.get_permissions_data_section = mock.Mock(return_value='get_perm')
        wikipermissionsresponse.set_permissions_request_section = mock.Mock(return_value='set_perm')
        request = req('POST', {'action': 'setperm'}, None, self.firstUser)
        result = wikipermissionsresponse.handle_permissions_request_section(request, self.wikiPages[0])
        self.assertIsNone(result)
        
    def test_handle_permissions_request_no_action(self):
        wikipermissionsresponse.get_sections = mock.Mock(return_value=[self.wikiSections[0], self.wikiSections[1]])
        wikipermissionsresponse.get_permissions_data_section = mock.Mock(return_value='get_perm')
        wikipermissionsresponse.set_permissions_request_section = mock.Mock(return_value='set_perm')
        request = req('POST', {}, None, self.firstUser)
        result = wikipermissionsresponse.handle_permissions_request_section(request, self.wikiPages[0])
        self.assertIsNone(result)

        
    def test_handle_permissions_request_action_is_wrong(self):
        wikipermissionsresponse.get_sections = mock.Mock(return_value=[self.wikiSections[0], self.wikiSections[1]])
        wikipermissionsresponse.get_permissions_data_section = mock.Mock(return_value='get_perm')
        wikipermissionsresponse.set_permissions_request_section = mock.Mock(return_value='set_perm')
        request = req('POST', {'action': 'qwetrty'}, None, self.firstUser)
        result = wikipermissionsresponse.handle_permissions_request_section(request, self.wikiPages[0])
        self.assertIsNone(result)

    def test_handle_permissions_request_get_request(self):
        wikipermissionsresponse.get_sections = mock.Mock(return_value=[self.wikiSections[0], self.wikiSections[1]])
        wikipermissionsresponse.get_permissions_data_section = mock.Mock(return_value='get_perm')
        wikipermissionsresponse.set_permissions_request_section = mock.Mock(return_value='set_perm')
        request = req('GET', None, {}, self.firstUser)
        result = wikipermissionsresponse.handle_permissions_request_section(request, self.wikiPages[0])
        self.assertEqual(result, 'get_perm')
        self.assertEqual(wikipermissionsresponse.get_permissions_data_section.call_count, 1)
        self.assertEqual(wikipermissionsresponse.get_sections.call_count, 1)

    def test_handle_permissions_request_post_setperm(self):
        wikipermissionsresponse.get_sections = mock.Mock(return_value=[self.wikiSections[0], self.wikiSections[1]])
        wikipermissionsresponse.get_permissions_data_section = mock.Mock(return_value='get_perm')
        wikipermissionsresponse.set_permissions_request_section = mock.Mock(return_value='set_perm')
        request = req('POST', {'action': 'setperm'}, None, self.firstUser)
        result = wikipermissionsresponse.handle_permissions_request_section(request, self.wikiPages[0])
        self.assertEqual(result, 'set_perm')
        self.assertEqual(wikipermissionsresponse.set_permissions_request_section.call_count, 1)
        self.assertEqual(wikipermissionsresponse.get_sections.call_count, 1)
