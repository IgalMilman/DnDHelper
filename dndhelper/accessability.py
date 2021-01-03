
from crum import get_current_user
from datamanagement.accessibility import \
    is_module_accessible as datamanagement_accessible
from django.shortcuts import reverse
from wiki.accessibility import is_module_accessible as wiki_accessible
from customcalendar.accessibility import is_module_accessible as calendar_accessible

def is_module_accessible(user=None)->bool:
    if user is None:
        user = get_current_user()
    if user is None:
        return False
    return user.is_superuser

def accessible_modules(user=None)->list:
    if user is None:
        user = get_current_user()
    if user is None:
        return {}
    return [{ 'label': 'Login', 'link': reverse('login'), 'accessible': not user.is_authenticated}, 
    { 'label': 'Personal Page', 'link': reverse('personal_page'), 'accessible': user.is_authenticated}, 
    { 'label': 'Wiki', 'link': reverse('wiki_homepage'), 'accessible': wiki_accessible(user)}, 
    { 'label': 'Calendar', 'link': reverse('calendar_homepage'), 'accessible': calendar_accessible(user)}, 
    { 'label': 'All events', 'link': reverse('calendar_events_table_page'), 'accessible': calendar_accessible(user)}, 
    { 'label': 'Data', 'link': reverse('datamanagement_homepage'), 'accessible': datamanagement_accessible(user)}, 
    ]