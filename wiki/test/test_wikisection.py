from django.test import TestCase
from wiki import wikisection
from wiki.wikipage import WikiPage, Keywords
from wiki.wikisection import WikiSection
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
import uuid, pytz, os
from datetime import datetime
from dndhelper.widget import quill
import mock

class WikiSectionTestCase(TestCase):
    def setUp(self):
        self.firstUser = User(is_superuser=True, username='test1', password='test1', email='test1@example.com', first_name='testname1', last_name='testlast2')
        self.secondUser = User(is_superuser=False, username='test2', password='test2', email='test2@example.com', first_name='testname2', last_name='testlast2')
        self.firstUser.save()
        self.secondUser.save()
        self.wikiuuid1 = uuid.uuid4()
        self.wikiuuid2 = uuid.uuid4()
        self.wikisqtext = '{"ops":[{"insert":"123123\\n"}]}'
        self.wikistext = 'text'
        self.wikisuuid1 = uuid.uuid4()
        self.wikisuuid2 = uuid.uuid4()
        self.wikisuuid3 = uuid.uuid4()
        self.wikipath = 'wiki'
        self.createdtime = datetime.now(pytz.utc)
        self.wikiPage1 = WikiPage(unid=self.wikiuuid1, createdon=self.createdtime, updatedon=self.createdtime, createdby=self.firstUser, updatedby=self.secondUser, title='testpage1')
        self.wikiPage2 = WikiPage(unid=self.wikiuuid2, createdon=self.createdtime, updatedon=self.createdtime, createdby=self.firstUser, updatedby=self.secondUser, title='testpage2')
        self.wikiPage1.save()
        self.wikiPage2.save()
        self.wikisection1 = WikiSection(unid=self.wikisuuid1, createdon=self.createdtime, updatedon=self.createdtime, createdby=self.firstUser, updatedby=self.secondUser, title='testsec1', pageorder=1, text=self.wikisqtext, wikipage=self.wikiPage1)
        self.wikisection2 = WikiSection(unid=self.wikisuuid2, createdon=self.createdtime, updatedon=self.createdtime, createdby=None, updatedby=None, title='testsec2', pageorder=2, text=self.wikistext, wikipage=self.wikiPage1)
        self.wikisection3 = WikiSection(unid=self.wikisuuid3, createdon=self.createdtime, updatedon=self.createdtime, createdby=self.firstUser, updatedby=self.secondUser, title='testsec3', pageorder=3, text=self.wikistext, wikipage=self.wikiPage1)
        self.wikisection1.save()
        self.wikisection1.createdon=self.createdtime
        self.wikisection1.updatedon=self.createdtime
        self.wikisection1.save()
        self.wikisection2.save()
        self.wikisection3.save()


    def test_wiki_section_get_files_folder(self):
        settings.WIKI_SECTION_FILES = self.wikipath
        os.makedirs = mock.Mock(return_value=None, spec='os.makedirs')
        os.path.exists = mock.Mock(return_value=False, spec='os.path.exists')
        self.assertEqual(self.wikisection1.get_files_folder(), os.path.join(self.wikipath, str(self.wikisuuid1)))
        os.path.exists.assert_called_once_with(os.path.join(self.wikipath, str(self.wikisuuid1)))
        os.makedirs.assert_called_once()

    def test_wiki_section_generate_link(self):
        wikisection.reverse = mock.Mock(return_value=self.wikipath, spec='django.urls.reverse')
        self.assertEqual(self.wikisection1.generate_link(), self.wikipath)
        wikisection.reverse.assert_called_once_with('wiki_page', kwargs={'wikipageuuid': self.wikiPage1.unid})

    def test_wiki_section_get_link(self):
        wikisection.reverse = mock.Mock(return_value=self.wikipath, spec='django.urls.reverse')
        self.assertEqual(self.wikisection1.get_link(), self.wikipath)
        wikisection.reverse.assert_called_once_with('wiki_page', kwargs={'wikipageuuid': self.wikiPage1.unid})

    def test_wiki_section_createtime(self):
        self.assertEqual(self.wikisection1.createtime(), self.createdtime.astimezone(pytz.timezone('America/New_York')))

    def test_wiki_section_updatetime(self):
        self.assertEqual(self.wikisection1.updatetime(), self.createdtime.astimezone(pytz.timezone('America/New_York')))

    def test_wiki_section_createuser(self):
        self.assertEqual(self.wikisection1.createuser(), self.firstUser.get_full_name())

    def test_wiki_section_updateuser(self):
        self.assertEqual(self.wikisection1.updateuser(), self.secondUser.get_full_name())

    def test_wiki_section_createuser_none(self):
        self.assertIsNone(self.wikisection2.createuser())

    def test_wiki_section_updateuser_none(self):
        self.assertIsNone(self.wikisection2.updateuser())

    def test_wiki_section_str(self):
        self.assertEqual(str(self.wikisection1), 'Wiki section: testsec1. UNID: ' + str(self.wikisuuid1))

    def test_wiki_section_is_quil_content_true(self):
        self.assertTrue(self.wikisection1.is_quill_content())

    def test_wiki_section_is_quil_content_false(self):
        self.assertFalse(self.wikisection2.is_quill_content())

    def test_wiki_section_get_content(self):
        self.assertEqual(self.wikisection2.get_content(), self.wikistext)

    def test_wiki_section_get_quill_content(self):
        self.assertEqual(self.wikisection1.get_quill_content(), quill.get_quill_text(self.wikisqtext))

    def test_wiki_page_get_sections_number_3(self):
        self.assertEqual(len(self.wikiPage1.wikisection_set.all()), 3)

    def test_wiki_page_get_sections_number_0(self):
        self.assertEqual(len(self.wikiPage2.wikisection_set.all()), 0)