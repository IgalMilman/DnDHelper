from django.test import TestCase
from wiki import modelgetters
from wiki.wikipage import WikiPage, Keywords
from wiki.wikisection import WikiSection
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
import uuid, pytz, os
from datetime import datetime, timedelta
from dndhelper.widget import quill
import mock

class WikiModelGettersTestCase(TestCase):
    def setUp(self):
        self.firstUser = User(is_superuser=True, username='test1', password='test1', email='test1@example.com', first_name='testname1', last_name='testlast2')
        self.secondUser = User(is_superuser=False, username='test2', password='test2', email='test2@example.com', first_name='testname2', last_name='testlast2')
        self.firstUser.save()
        self.secondUser.save()
        self.wikiuuid = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
        self.wikistext = ['{"ops":[{"insert":"123123\\n"}]}', 'text', None]
        self.wikisuuid = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
        self.wikipath = 'wiki'
        self.createdtime = datetime.now(pytz.utc)
        self.wikiPages = []
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
            if i==1:
                self.wikiSections[1].createdby = None
                self.wikiSections[1].updatedby = None
            self.wikiSections[i].save()

    def test_form_all_wiki_pages_data_success(self):
        self.wikiPages.reverse()
        self.assertListEqual(list(modelgetters.form_all_wiki_pages_data(self.firstUser)['wiki_pages']), self.wikiPages)

    def test_form_all_wiki_pages_data_fail_permission(self):
        self.assertListEqual(list(modelgetters.form_all_wiki_pages_data(self.secondUser)['wiki_pages']), [])

    def test_form_all_wiki_pages_data_failed(self):
        with mock.patch('wiki.wikipage.WikiPage.objects.all') as failmock:
            failmock.side_effect = Exception("random error")
            self.assertIsNone(modelgetters.form_all_wiki_pages_data(self.firstUser))
    
    def test_form_get_one_wiki_page_data_success_3(self):
        result = modelgetters.get_one_wiki_page_data(self.wikiPages[0].unid, self.firstUser)
        self.assertEqual(result['wiki_page'], self.wikiPages[0])
        self.assertListEqual(list(result['wiki_page_sections']), self.wikiSections)
    
    def test_form_get_one_wiki_page_data_success_2_common_knowledge(self):
        self.wikiSections[0].commonknowledge = True
        self.wikiSections[0].save()
        self.wikiSections[1].commonknowledge = True
        self.wikiSections[1].save()
        result = modelgetters.get_one_wiki_page_data(self.wikiPages[0].unid, self.secondUser)
        self.assertEqual(result['wiki_page'], self.wikiPages[0])
        self.assertListEqual(list(result['wiki_page_sections']), self.wikiSections[0:2])
    
    def test_form_get_one_wiki_page_data_fail_permission(self):
        result = modelgetters.get_one_wiki_page_data(self.wikiPages[0].unid, self.secondUser)
        self.assertIsNone(result)
        
    def test_form_get_one_wiki_page_data_success_0(self):
        result = modelgetters.get_one_wiki_page_data(self.wikiPages[1].unid, self.firstUser)
        self.assertEqual(result['wiki_page'], self.wikiPages[1])
        self.assertListEqual(list(result['wiki_page_sections']), [])

    def test_form_get_one_wiki_page_data_fail_no_page(self):
        self.assertIsNone(modelgetters.get_one_wiki_page_data(uuid.uuid4(), self.firstUser))

    def test_form_get_one_wiki_page_data_fail_error(self):
        with mock.patch('wiki.wikipage.WikiPage.objects.get') as failmock:
            failmock.side_effect = Exception("random error")
            self.assertIsNone(modelgetters.get_one_wiki_page_data(self.wikiPages[0].unid, self.firstUser))