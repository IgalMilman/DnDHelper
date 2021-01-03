"""Wiki URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path, re_path, reverse_lazy

from customcalendar import views as calendar_views

urlpatterns = [
    path('', calendar_views.calendarHomePage, name='calendar_homepage'),
    path('event/<uuid:ceventuuid>', calendar_views.calendarEventPage, name='calendar_event_page'),
    path('event/<uuid:ceventuuid>/perm', calendar_views.eventPermissionsAjaxRequestHandle, name='calendar_event_perm'),
    path('event/edit', calendar_views.calendarEventPageForm, name='calendar_event_form_page'),
    path('events/<int:year>', calendar_views.calendarAllEventsAPI, name='calendar_all_events'),
    path('a/event/<uuid:ceventuuid>', calendar_views.calendarEventPageAPI, name='calendar_event_api'),
    path('event/<uuid:ceventuuid>/f/', calendar_views.calendarHomePage, name='calendar_event_page_file_empty'),
    path('event/<uuid:ceventuuid>/f/<filename>', calendar_views.calendarHomePage, name='calendar_event_page_file'),

    path('date/update', calendar_views.calendarUpdateDateAjaxRequest, name='calendar_date_update'),
    path('settings', calendar_views.calendarSettingsPage, name='calendar_settings'),
    path('settings/general', calendar_views.calendarSettingsGeneralAjaxRequest, name='calendar_settings_general'),
    path('settings/months', calendar_views.calendarSettingsMonthAjaxRequest, name='calendar_settings_month'),
    path('settings/months/<int:monthid>', calendar_views.calendarSettingsMonthAjaxRequest, name='calendar_settings_month'),
    path('settings/week', calendar_views.calendarSettingsWeekAjaxRequest, name='calendar_settings_week'),
    path('settings/week/<int:weekdayid>', calendar_views.calendarSettingsWeekDayAjaxRequest, name='calendar_settings_weekday'),
    path('settings/weekday', calendar_views.calendarSettingsWeekDayAjaxRequest, name='calendar_settings_weekday_new'),
]
