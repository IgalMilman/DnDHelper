import os
import uuid
from datetime import datetime

import mock
import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from wiki.models import wikipage, wikisection
from wiki.models.wikipage import Keywords, WikiPage


class WikiPageTestCase(TestCase):
    def setUp(self):
        self.firstUser = User(is_superuser=True, username='test1', password='test1', email='test1@example.com', first_name='testname1', last_name='testlast1')
        self.secondUser = User(is_superuser=False, username='test2', password='test2', email='test2@example.com', first_name='testname2', last_name='testlast2')
        self.wikiuuid = uuid.uuid4()
        self.wikipath = 'wiki'
        self.createdtime = datetime.now(pytz.utc)
        self.wikiPage = WikiPage(unid=self.wikiuuid, createdon=self.createdtime, updatedon=self.createdtime, createdby=self.firstUser, updatedby=self.secondUser, title='testpage')
        self.wikiPageNone = WikiPage(unid=self.wikiuuid, createdon=self.createdtime, updatedon=self.createdtime, createdby=None, updatedby=None, title='testpage')


    def test_wiki_page_get_files_folder(self):
        settings.WIKI_FILES = self.wikipath
        os.makedirs = mock.Mock(return_value=None, spec='os.makedirs')
        os.path.exists = mock.Mock(return_value=False, spec='os.path.exists')
        self.assertEqual(self.wikiPage.get_files_folder(), os.path.join(self.wikipath, str(self.wikiuuid)))
        os.path.exists.assert_called_once_with(os.path.join(self.wikipath, str(self.wikiuuid)))
        os.makedirs.assert_called_once()

    def test_wiki_page_generate_link(self):
        wikipage.reverse = mock.Mock(return_value=self.wikipath, spec='django.urls.reverse')
        self.assertEqual(self.wikiPage.generate_link(), self.wikipath)
        wikipage.reverse.assert_called_once_with('wiki_page', kwargs={'wikipageuuid': self.wikiuuid})

    def test_wiki_page_get_link(self):
        wikipage.reverse = mock.Mock(return_value=self.wikipath, spec='django.urls.reverse')
        self.assertEqual(self.wikiPage.get_link(), self.wikipath)
        wikipage.reverse.assert_called_once_with('wiki_page', kwargs={'wikipageuuid': self.wikiuuid})

    def test_wiki_page_createtime(self):
        self.assertEqual(self.wikiPage.createtime(), self.createdtime.astimezone(pytz.timezone('America/New_York')))

    def test_wiki_page_updatetime(self):
        self.assertEqual(self.wikiPage.updatetime(), self.createdtime.astimezone(pytz.timezone('America/New_York')))

    def test_wiki_page_createuser(self):
        self.assertEqual(self.wikiPage.createuser(), self.firstUser.get_full_name())

    def test_wiki_page_updateuser(self):
        self.assertEqual(self.wikiPage.updateuser(), self.secondUser.get_full_name())

    def test_wiki_page_createuser_none(self):
        self.assertIsNone(self.wikiPageNone.createuser())

    def test_wiki_page_updateuser_none(self):
        self.assertIsNone(self.wikiPageNone.updateuser())

    def test_wiki_page_str(self):
        self.assertEqual(str(self.wikiPage), 'Wiki title: testpage. UNID: ' + str(self.wikiuuid))
