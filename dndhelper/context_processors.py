from datamanagement.accessibility import \
    is_module_accessible as datamanagement_accessible
from django.conf import settings
from django.shortcuts import reverse
from wiki.accessibility import is_module_accessible as wiki_accessible
from customcalendar.accessibility import is_module_accessible as calendar_accessible


def global_settings(request):
    return {
        'VERSION_STATIC_FILES': True if settings.VERSION_STATIC_FILES else False,
        'PROGRAM_VERSION': settings.SOFTWARE_VERSION,
        'URL_ADD_TO_STATIC_FILES': '?v='+settings.STATIC_FILES_VERSION if settings.VERSION_STATIC_FILES else '',
        'needdatatables': False,
        'needquillinput': False,
        'EMAIL_URL_FOR_LINKS': settings.EMAIL_HOST_LINK,
        'LOGO_ALT_NAME': settings.SOFTWARE_NAME,
        'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
        'SOFTWARE_NAME': settings.SOFTWARE_NAME,
        'SOFTWARE_NAME_SHORT': settings.SOFTWARE_NAME_SHORT,
        'MENU_ITEMS': [{ 'label': 'Homepage', 'link': reverse('homepage'), 'accessible': True}, 
{ 'label': 'Login', 'link': reverse('login'), 'accessible': not request.user.is_authenticated}, 
{ 'label': 'Wiki', 'link': reverse('wiki_homepage'), 'accessible': wiki_accessible(request.user)}, 
{ 'label': 'Calendar', 'link': reverse('calendar_homepage'), 'accessible': calendar_accessible(request.user)}, 
{ 'label': 'Data', 'link': reverse('datamanagement_homepage'), 'accessible': datamanagement_accessible(request.user)}, 
],
    }
