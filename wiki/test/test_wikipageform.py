import os
import uuid
from datetime import datetime, timedelta

import mock
import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from utils.widget import quill
from wiki.forms import wikipageform
from wiki.models import wikipage, wikisection
from wiki.models.permissionpage import PermissionPage
from wiki.models.permissionsection import PermissionSection
from wiki.models.wikipage import Keywords, WikiPage
from wiki.models.wikisection import WikiSection


def render_mock(request, template, data, content_type='test'):
    return {'request':request, 'template':template, 'data': data, 'content_type':content_type}

def redirect_mock(link):
    return link

def reverse_mock(link, kwargs=None):
    if kwargs is None:
        return link
    return link

class req:
    def __init__(self, method='GET', post={}, user=None):
        self.method = method
        self.user = user
        self.POST = post


class WikiPageFormTestCase(TestCase):
    def setUp(self):
        self.firstUser = User(is_superuser=True, username='test1', password='test1', email='test1@example.com', first_name='testname1', last_name='testlast2')
        self.secondUser = User(is_superuser=False, username='test2', password='test2', email='test2@example.com', first_name='testname2', last_name='testlast2')
        self.thirdUser = User(is_superuser=False, username='test3', password='test3', email='test3@example.com', first_name='testname3', last_name='testlast3')
        self.fourthUser = User(is_superuser=False, username='test4', password='test4', email='test4@example.com', first_name='testname4', last_name='testlast4')        
        self.firstUser.save()
        self.secondUser.save()        
        self.thirdUser.save()
        self.fourthUser.save()
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
        for i in range(3):
            self.wikiPages.append(WikiPage(unid=self.wikiuuid[i], createdon=self.createdtime, updatedon=self.createdtime, createdby=self.firstUser, updatedby=self.secondUser, title='testpage'+str(i+1)))
            self.wikiPages[i].save()
            self.wikiPages[i].createdon=self.createdtime + timedelta(hours=i)
            self.wikiPages[i].updatedon=self.createdtime + timedelta(hours=i)
            self.wikiPages[i].save()
        self.pagepermissions = []
        pagep = PermissionPage(createdby=self.firstUser, accesslevel=20, grantedto=self.thirdUser, wikipage=self.wikiPages[2])
        pagep.save()
        self.pagepermissions.append(pagep)
        pagep = PermissionPage(createdby=self.firstUser, accesslevel=30, grantedto=self.fourthUser, wikipage=self.wikiPages[2])
        pagep.save()
        self.pagepermissions.append(pagep)
        self.wikiSections = []
        for i in range(3):
            self.wikiSections.append(WikiSection(unid=self.wikisuuid[i], createdon=self.createdtime, updatedon=self.createdtime, createdby=self.firstUser, updatedby=self.secondUser, title='testsec'+str(i+1), pageorder=i+1, text=self.wikistext[i], wikipage=self.wikiPages[0]))
            self.wikiSections[i].save()
            self.wikiSections[i].createdon=self.createdtime + timedelta(hours=i)
            self.wikiSections[i].updatedon=self.createdtime + timedelta(hours=i)
            perm = PermissionSection(createdby=self.firstUser, accesslevel=20, grantedto=self.secondUser, section=self.wikiSections[i])
            perm.save()
            self.permissions.append(perm)
            perm = PermissionSection(createdby=self.firstUser, accesslevel=10, grantedto=self.thirdUser, section=self.wikiSections[i])
            perm.save()
            self.permissions.append(perm)
            if i==1:
                self.wikiSections[1].createdby = None
                self.wikiSections[1].updatedby = None
            self.wikiSections[i].save()
        settings.SOFTWARE_NAME_SHORT = self.softwarename
        wikipageform.settings.SOFTWARE_NAME_SHORT = self.softwarename
        wikipageform.settings.WIKI_FILES = self.wikipath
        os.path.exists = mock.Mock(return_value=True, spec='os.path.exists')
        os.makedirs = mock.Mock(return_value=None, spec='os.makedirs')
        wikipageform.render = mock.Mock(side_effect=render_mock)
        wikipageform.redirect = mock.Mock(side_effect=redirect_mock)
        wikipageform.reverse = mock.Mock(side_effect=reverse_mock)
        wikipage.reverse = mock.Mock(side_effect=reverse_mock)


    def test_wiki_page_form_get_request_super_user(self):
        post = {'action':'add'}
        method = 'GET'
        request = req(method=method, user=self.firstUser)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'add')
        self.assertEqual(data['PAGE_TITLE'], 'Post an article: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Post Article')
        self.assertEqual(data['submbutton'], 'Post article')
        self.assertEqual(data['backurl'], self.wikimainpagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikipageform.WikiPageForm)
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_get_request_no_access(self):
        method = 'GET'
        request = req(method=method, user=self.thirdUser)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_get_request_no_permissions(self):
        method = 'GET'
        request = req(method=method, user=self.fourthUser)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_post_request_no_action(self):
        post = {}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'add')
        self.assertEqual(data['PAGE_TITLE'], 'Post an article: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Post Article')
        self.assertEqual(data['submbutton'], 'Post article')
        self.assertEqual(data['backurl'], self.wikimainpagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikipageform.WikiPageForm)
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_post_request_no_action_no_permissions(self):
        post = {}
        method = 'POST'
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_add_request_success(self):
        post = {'action':'add', 'title':self.wikiPages[0].title}
        method = 'POST'
        WikiPage.objects.all().delete()
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikipagelink)
        self.assertEqual(len(WikiPage.objects.all()), 1)
        wiki = WikiPage.objects.all()[0]
        self.assertEqual(wiki.title, self.wikiPages[0].title)
        self.assertEqual(wiki.createdby, self.firstUser)
        self.assertEqual(wiki.updatedby, self.firstUser)

    def test_wiki_page_form_add_request_failed_no_access(self):
        post = {'action':'add', 'title':self.wikiPages[0].title}
        method = 'POST'
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_add_request_failed_no_permissions(self):
        post = {'action':'add', 'title':self.wikiPages[0].title}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_add_request_failed_no_title(self):
        post = {'action':'add', 'title':None}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'add')
        self.assertEqual(data['PAGE_TITLE'], 'Post an article: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Post Article')
        self.assertEqual(data['submbutton'], 'Post article')
        self.assertEqual(data['backurl'], self.wikimainpagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikipageform.WikiPageForm)
        self.assertTrue(('title' in data['form'].data) or (data['form'].data == {}))
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_change_request_success_super_user(self):
        post = {'action':'change', 'targetid': self.wikiPages[0].unid}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'changed')
        self.assertEqual(data['targetid'], self.wikiPages[0].unid)
        self.assertEqual(data['PAGE_TITLE'], 'Post an article: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Change Posted Article')
        self.assertEqual(data['submbutton'], 'Change posted article')
        self.assertEqual(data['deletebutton'], 'Delete article')
        self.assertEqual(data['backurl'], self.wikipagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikipageform.WikiPageForm)
        self.assertTrue('title' in data['form'].initial)
        self.assertEqual(data['form'].initial['title'], self.wikiPages[0].title)
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_change_request_success_permission(self):
        post = {'action':'change', 'targetid': self.wikiPages[2].unid}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'changed')
        self.assertEqual(data['targetid'], self.wikiPages[2].unid)
        self.assertEqual(data['PAGE_TITLE'], 'Post an article: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Change Posted Article')
        self.assertEqual(data['submbutton'], 'Change posted article')
        self.assertEqual(data['deletebutton'], 'Delete article')
        self.assertEqual(data['backurl'], self.wikipagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikipageform.WikiPageForm)
        self.assertTrue('title' in data['form'].initial)
        self.assertEqual(data['form'].initial['title'], self.wikiPages[2].title)
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_change_request_fail_no_access(self):
        post = {'action':'change', 'targetid': self.wikiPages[0].unid}
        method = 'POST'
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_change_request_fail_no_permissions(self):
        post = {'action':'change', 'targetid': self.wikiPages[0].unid}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_change_request_fail_no_page(self):
        post = {'action':'change', 'targetid':uuid.uuid4()}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_change_request_fail_no_target_id(self):
        post = {'action':'change'}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_changed_request_success_super_user(self):
        post = {'action':'changed', 'targetid': self.wikiPages[0].unid, 'title':'new title'}
        method = 'POST'
        self.wikiPages[0].updatedby = self.secondUser
        self.wikiPages[0].save()
        wiki = WikiPage.objects.get(unid=self.wikiPages[0].unid)
        self.assertEqual(wiki.updatedby, self.secondUser)
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikipagelink)
        wiki = WikiPage.objects.get(unid=self.wikiPages[0].unid)
        self.assertEqual(wiki.title, 'new title')
        self.assertEqual(wiki.createdby, self.firstUser)
        self.assertEqual(wiki.updatedby, self.firstUser)
        self.assertNotEqual(wiki.updatedon, wiki.createdon)

    def test_wiki_page_form_changed_request_success_permissions(self):
        post = {'action':'changed', 'targetid': self.wikiPages[2].unid, 'title':'new title'}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikipagelink)
        wiki = WikiPage.objects.get(unid=self.wikiPages[2].unid)
        self.assertEqual(wiki.title, 'new title')
        self.assertEqual(wiki.createdby, self.firstUser)
        self.assertEqual(wiki.updatedby, self.fourthUser)
        self.assertNotEqual(wiki.updatedon, wiki.createdon)

    def test_wiki_page_form_changed_request_failed_no_access(self):
        post = {'action':'changed', 'targetid': self.wikiPages[0].unid, 'title':'new title'}
        method = 'POST'
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_changed_request_failed_no_permissions(self):
        post = {'action':'changed', 'targetid': self.wikiPages[0].unid, 'title':'new title'}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_changed_request_failed_no_title(self):
        post = {'action':'changed', 'targetid': self.wikiPages[0].unid, 'title': None}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'changed')
        self.assertEqual(data['targetid'], self.wikiPages[0].unid)
        self.assertEqual(data['PAGE_TITLE'], 'Post an article: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Change Posted Article')
        self.assertEqual(data['submbutton'], 'Change posted article')
        self.assertEqual(data['deletebutton'], 'Delete article')
        self.assertEqual(data['backurl'], self.wikipagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikipageform.WikiPageForm)
        self.assertTrue('title' in data['form'].initial)
        self.assertEqual(data['form'].initial['title'], self.wikiPages[0].title)
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_changed_request_fail_no_page(self):
        post = {'action':'changed', 'targetid':uuid.uuid4()}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_changed_request_fail_no_target_id(self):
        post = {'action':'changed'}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_delete_request_success_super_user(self):
        post = {'action':'delete', 'targetid':self.wikiPages[0].unid}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)
        try:
            wiki = WikiPage.objects.get(unid=self.wikiPages[0].unid)
        except:
            wiki=None
        self.assertIsNone(wiki)

    def test_wiki_page_form_delete_request_success_permission(self):
        post = {'action':'delete', 'targetid':self.wikiPages[2].unid}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)
        try:
            wiki = WikiPage.objects.get(unid=self.wikiPages[2].unid)
        except:
            wiki=None
        self.assertIsNone(wiki)

    def test_wiki_page_form_delete_request_fail_wrong_action(self):
        post = {'action':'qwertyu', 'targetid':self.wikiPages[0].unid}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_delete_request_fail_no_access(self):
        post = {'action':'delete', 'targetid':self.wikiPages[0].unid}
        method = 'POST'
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_delete_request_fail_no_permissions(self):
        post = {'action':'delete', 'targetid':self.wikiPages[0].unid}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_delete_request_fail_no_page(self):
        post = {'action':'delete', 'targetid':uuid.uuid4()}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_delete_request_fail_no_target_id(self):
        post = {'action':'delete'}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikipageform.WikiArticleFormParse(request)
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_viewable_super_user(self):
        self.assertTrue(self.wikiPages[0].viewable(self.firstUser))

    def test_wiki_page_viewable_permission_editable(self):
        self.assertTrue(self.wikiPages[0].viewable(self.secondUser))

    def test_wiki_page_viewable_permission_viewable(self):
        self.assertTrue(self.wikiPages[0].viewable(self.thirdUser))

    def test_wiki_page_not_viewable_permission(self):
        self.assertFalse(self.wikiPages[0].viewable(self.fourthUser))

    def test_wiki_page_viewable_common_knowledge(self):
        self.wikiPages[0].commonknowledge = True
        self.wikiPages[0].save()
        self.assertTrue(self.wikiPages[0].viewable(self.fourthUser))
