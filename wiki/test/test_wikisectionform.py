from django.test import TestCase
from wiki import wikisectionform
from wiki import wikipage
from wiki import wikisection
from wiki.permissionsection import PermissionSection 
from wiki.wikipage import WikiPage, Keywords
from wiki.wikisection import WikiSection
from django.contrib.auth.models import User
from django.conf import settings
import uuid, pytz, os, copy
from datetime import datetime, timedelta
from dndhelper.widget import quill
import mock

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


class WikiSectionFormTestCase(TestCase):
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
            self.permissions.append(perm)
            perm = PermissionSection(createdby=self.firstUser, accesslevel=30, grantedto=self.secondUser, section=self.wikiSections[i])
            perm.save()
            self.permissions.append(perm)
            if i==1:
                self.wikiSections[1].createdby = None
                self.wikiSections[1].updatedby = None
            self.wikiSections[i].save()
        settings.SOFTWARE_NAME_SHORT = self.softwarename
        wikisectionform.settings.SOFTWARE_NAME_SHORT = self.softwarename
        os.path.exists = mock.Mock(return_value=True, spec='os.path.exists')
        os.makedirs = mock.Mock(return_value=None, spec='os.makedirs')
        wikisectionform.render = mock.Mock(side_effect=render_mock)
        wikisectionform.redirect = mock.Mock(side_effect=redirect_mock)
        wikisectionform.reverse = mock.Mock(side_effect=reverse_mock)
        wikipage.reverse = mock.Mock(side_effect=reverse_mock)
        wikisection.reverse = mock.Mock(side_effect=reverse_mock)
        

    def test_wiki_page_form_get_request_no_page(self):
        post = {'action':'delete'}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, uuid.uuid4())
        self.assertEqual(result, self.wikimainpagelink)

    def test_wiki_page_form_get_request_super_user(self):
        post = {'action':'add'}
        method = 'GET'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'add')
        self.assertEqual(data['PAGE_TITLE'], 'Add section: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Add Section')
        self.assertEqual(data['submbutton'], 'Add section')
        self.assertEqual(data['backurl'], self.wikipagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikisectionform.WikiSectionForm)
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_get_request_no_access(self):
        method = 'GET'
        request = req(method=method, user=self.thirdUser)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_get_request_no_permissions(self):
        method = 'GET'
        request = req(method=method, user=self.fourthUser)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_post_request_no_action_super_user(self):
        post = {}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'add')
        self.assertEqual(data['PAGE_TITLE'], 'Add section: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Add Section')
        self.assertEqual(data['submbutton'], 'Add section')
        self.assertEqual(data['backurl'], self.wikipagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikisectionform.WikiSectionForm)
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_post_request_no_action_no_access(self):
        post = {}
        method = 'POST'
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_post_request_no_action_no_permissions(self):
        post = {}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_add_request_success(self):
        form = wikisectionform.WikiSectionForm(instance=self.wikiSections[0])
        post = form.initial
        post['action'] = 'add'
        method = 'POST'
        WikiSection.objects.all().delete()
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)
        self.assertEqual(len(WikiSection.objects.all()), 1)
        wikis = WikiSection.objects.all()[0]
        self.assertEqual(wikis.title, self.wikiSections[0].title)
        self.assertEqual(wikis.text, self.wikiSections[0].text)
        self.assertEqual(wikis.pageorder, self.wikiSections[0].pageorder)
        self.assertEqual(wikis.createdby, self.firstUser)
        self.assertEqual(wikis.updatedby, self.firstUser)

    def test_wiki_page_form_add_request_fail_no_access(self):
        form = wikisectionform.WikiSectionForm(instance=self.wikiSections[0])
        post = form.initial
        post['action'] = 'add'
        method = 'POST'
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_add_request_fail_no_permissions(self):
        form = wikisectionform.WikiSectionForm(instance=self.wikiSections[0])
        post = form.initial
        post['action'] = 'add'
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_add_request_failed_no_title(self):
        post = {'action':'add', 'title':None}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'add')
        self.assertEqual(data['PAGE_TITLE'], 'Add section: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Add Section')
        self.assertEqual(data['submbutton'], 'Add section')
        self.assertEqual(data['backurl'], self.wikipagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikisectionform.WikiSectionForm)
        self.assertTrue(('title' in data['form'].data) or (data['form'].data == {}))
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_change_request_success(self):
        post = {'action':'change', 'targetid': self.wikiSections[0].unid}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'changed')
        self.assertEqual(data['targetid'], self.wikiSections[0].unid)
        self.assertEqual(data['PAGE_TITLE'], 'Change section: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Change Section')
        self.assertEqual(data['submbutton'], 'Change section')
        self.assertEqual(data['deletebutton'], 'Delete section')
        self.assertEqual(data['backurl'], self.wikipagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikisectionform.WikiSectionForm)
        self.assertTrue('title' in data['form'].initial)
        self.assertEqual(data['form'].initial['title'], self.wikiSections[0].title)
        self.assertEqual(data['form'].initial['pageorder'], self.wikiSections[0].pageorder)
        self.assertEqual(data['form'].initial['text'], self.wikiSections[0].text)
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_change_request_fail_no_access(self):
        post = {'action':'change', 'targetid': self.wikiSections[0].unid}
        method = 'POST'
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_change_request_fail_no_permissions(self):
        post = {'action':'change', 'targetid': self.wikiSections[0].unid}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_change_request_fail_no_section(self):
        post = {'action':'change', 'targetid':uuid.uuid4()}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_change_request_fail_no_target_id(self):
        post = {'action':'change'}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_changed_request_success_super_user(self):
        form = wikisectionform.WikiSectionForm(instance=self.wikiSections[1])
        post = form.initial
        post['action'] = 'changed'
        post['targetid'] = self.wikiSections[0].unid
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)
        wikis = WikiSection.objects.get(unid=self.wikiSections[0].unid)
        self.assertEqual(wikis.title, self.wikiSections[1].title)
        self.assertEqual(wikis.pageorder, self.wikiSections[1].pageorder)
        self.assertEqual(wikis.createdby, self.firstUser)
        self.assertEqual(wikis.updatedby, self.firstUser)
        self.assertNotEqual(wikis.updatedon, wikis.createdon)

    def test_wiki_page_form_changed_request_success_permissions(self):
        form = wikisectionform.WikiSectionForm(instance=self.wikiSections[1])
        post = form.initial
        post['action'] = 'changed'
        post['targetid'] = self.wikiSections[0].unid
        method = 'POST'
        request = req(method=method, user=self.secondUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)
        wikis = WikiSection.objects.get(unid=self.wikiSections[0].unid)
        self.assertEqual(wikis.title, self.wikiSections[1].title)
        self.assertEqual(wikis.pageorder, self.wikiSections[1].pageorder)
        self.assertEqual(wikis.createdby, self.firstUser)
        self.assertEqual(wikis.updatedby, self.secondUser)
        self.assertNotEqual(wikis.updatedon, wikis.createdon)

    def test_wiki_page_form_changed_request_fail_no_access(self):
        form = wikisectionform.WikiSectionForm(instance=self.wikiSections[1])
        post = form.initial
        post['action'] = 'changed'
        post['targetid'] = self.wikiSections[0].unid
        method = 'POST'
        oldsection = copy.deepcopy(self.wikiSections[0])
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)
        wikis = WikiSection.objects.get(unid=self.wikiSections[0].unid)
        self.assertEqual(wikis.title, oldsection.title)
        self.assertEqual(wikis.pageorder, oldsection.pageorder)
        self.assertEqual(wikis.createdby, oldsection.createdby)
        self.assertEqual(wikis.updatedby, oldsection.updatedby)
        self.assertEqual(wikis.updatedon, oldsection.updatedon)

    def test_wiki_page_form_changed_request_fail_no_permissions(self):
        form = wikisectionform.WikiSectionForm(instance=self.wikiSections[1])
        post = form.initial
        post['action'] = 'changed'
        post['targetid'] = self.wikiSections[0].unid
        method = 'POST'
        oldsection = copy.deepcopy(self.wikiSections[0])
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)
        wikis = WikiSection.objects.get(unid=self.wikiSections[0].unid)
        self.assertEqual(wikis.title, oldsection.title)
        self.assertEqual(wikis.pageorder, oldsection.pageorder)
        self.assertEqual(wikis.createdby, oldsection.createdby)
        self.assertEqual(wikis.updatedby, oldsection.updatedby)
        self.assertEqual(wikis.updatedon, oldsection.updatedon)

    def test_wiki_page_form_changed_request_failed_no_title(self):
        post = {'action':'changed', 'targetid': self.wikiSections[0].unid, 'title': None}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result['request'], request)
        self.assertEqual(result['template'], self.formtemplate)
        data = result['data']
        self.assertEqual(data['action'], 'changed')
        self.assertEqual(data['targetid'], self.wikiSections[0].unid)
        self.assertEqual(data['PAGE_TITLE'], 'Change section: ' + self.softwarename)
        self.assertEqual(data['minititle'], 'Change Section')
        self.assertEqual(data['submbutton'], 'Change section')
        self.assertEqual(data['deletebutton'], 'Delete section')
        self.assertEqual(data['backurl'], self.wikipagelink)
        self.assertEqual(data['needquillinput'], True)
        self.assertIsInstance(data['form'], wikisectionform.WikiSectionForm)
        self.assertTrue('title' in data['form'].initial)
        self.assertEqual(data['form'].initial['title'], self.wikiSections[0].title)
        self.assertEqual(data['form'].initial['pageorder'], self.wikiSections[0].pageorder)
        self.assertEqual(data['form'].initial['text'], self.wikiSections[0].text)
        self.assertEqual(result['content_type'], self.contenttype)

    def test_wiki_page_form_changed_request_fail_no_page(self):
        post = {'action':'changed', 'targetid':uuid.uuid4()}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_changed_request_fail_no_target_id(self):
        post = {'action':'changed'}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_delete_request_success_super_user(self):
        post = {'action':'delete', 'targetid':self.wikiSections[0].unid}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)
        try:
            wikis = WikiSection.objects.get(unid=self.wikiSections[0].unid)
        except:
            wikis=None
        self.assertIsNone(wikis)

    def test_wiki_page_form_delete_request_success_permissions(self):
        post = {'action':'delete', 'targetid':self.wikiSections[0].unid}
        method = 'POST'
        request = req(method=method, user=self.secondUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)
        try:
            wikis = WikiSection.objects.get(unid=self.wikiSections[0].unid)
        except:
            wikis=None
        self.assertIsNone(wikis)

    def test_wiki_page_form_delete_request_fail_no_access(self):
        post = {'action':'delete', 'targetid':self.wikiSections[0].unid}
        method = 'POST'
        request = req(method=method, user=self.thirdUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        try:
            wikis = WikiSection.objects.get(unid=self.wikiSections[0].unid)
        except:
            wikis=None
        self.assertIsNotNone(wikis)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_delete_request_fail_no_permissions(self):
        post = {'action':'delete', 'targetid':self.wikiSections[0].unid}
        method = 'POST'
        request = req(method=method, user=self.fourthUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        try:
            wikis = WikiSection.objects.get(unid=self.wikiSections[0].unid)
        except:
            wikis=None
        self.assertIsNotNone(wikis)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_delete_request_fail_no_page(self):
        post = {'action':'delete', 'targetid':uuid.uuid4()}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)

    def test_wiki_page_form_delete_request_fail_no_target_id(self):
        post = {'action':'delete'}
        method = 'POST'
        request = req(method=method, user=self.firstUser, post=post)
        result = wikisectionform.WikiSectionFormParse(request, self.wikiPages[0].unid)
        self.assertEqual(result, self.wikipagelink)
