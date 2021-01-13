from datetime import datetime

import pytz
from customcalendar.modelgetters import get_calendar
from customcalendar.models.calendarevent import CEvent
from django import forms
from django.shortcuts import redirect, render
from django.urls import reverse
from dndhelper import settings
from dndhelper import views as main_views
from utils.widget import form_switch, quill


class CEventForm(forms.ModelForm):
    eventmonth = forms.ChoiceField(label="Event month")
    text = quill.QuillField(label="Event text", widget=quill.QuillWidget({'toolbar': {'image': True, 'video': True}}), required=False)
    commonknowledge = form_switch.SwitchOnOffField(label="Is public knowledge?", required=False)

    class Meta:
        model = CEvent
        fields = ('title','eventday','eventmonth','eventyear', 'eventtype', 'commonknowledge', 'text', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cal = get_calendar()
        self.fields['eventmonth'].choices = cal.months_array()
        if 'instance' in kwargs:
            self.fields['text'].widget.quillobject = kwargs['instance']
            cetype = CEvent.create_types(None, event=kwargs['instance'])
            self.fields['eventtype'].choices = cetype
        else:
            self.fields['eventday'].initial = cal.currentday
            self.fields['eventmonth'].initial = cal.currentmonth
            self.fields['eventyear'].initial = cal.currentyear
            cetype = CEvent.create_types(None)
            self.fields['eventtype'].choices = cetype

def CEventFormParse(request):
    data={}
    data['PAGE_TITLE'] = 'Change posted event: ' + settings.SOFTWARE_NAME_SHORT
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            if not CEvent.cancreate(request.user):
                return redirect(reverse('calendar_homepage'))
            form = CEventForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.createdby = request.user
                model.updatedby = request.user
                model.save()
                return redirect(model.get_link())
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'Post an event: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Post Event'
                data['submbutton'] = 'Post event'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curpost=CEvent.objects.get(unid=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('calendar_homepage'))
                if not curpost.editable(request.user):
                    return redirect(reverse('calendar_homepage'))
                form = CEventForm(instance=curpost)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Post an event: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Change Posted Event'
                data['submbutton'] = 'Change posted event'
                data['backurl'] = curpost.get_link()
                data['deletebutton'] = 'Delete event'
            else:
                return redirect(reverse('calendar_homepage'))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curpost=CEvent.objects.get(unid=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('calendar_homepage'))
                if not curpost.editable(request.user):
                    return redirect(reverse('calendar_homepage'))
                form = CEventForm(request.POST, instance=curpost)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.updatedby = request.user
                    model.updatedon = datetime.now(pytz.utc)
                    model.save()
                    return redirect(model.get_link())
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Post an event: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Change Posted Event'
                data['submbutton'] = 'Change posted event'
                data['backurl'] = curpost.get_link()
                data['deletebutton'] = 'Delete event'
            else:
                return redirect(reverse('calendar_homepage'))
        elif (request.POST['action']=='delete'): 
            if('targetid' in request.POST):
                try:
                    curpost=CEvent.objects.get(unid=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('calendar_homepage'))
                if not curpost.editable(request.user):
                    return redirect(reverse('calendar_homepage'))
                curpost.delete()
                return redirect(reverse('calendar_homepage'))
            else:
                return redirect(reverse('calendar_homepage'))
        else:
            return redirect(reverse('calendar_homepage'))
    else:
        if not CEvent.cancreate(request.user):
            return redirect(reverse('calendar_homepage'))
        form = CEventForm()
        data['action']='add'
        data['PAGE_TITLE'] = 'Post an event: ' + settings.SOFTWARE_NAME_SHORT
        data['minititle'] = 'Post Event'
        data['submbutton'] = 'Post event'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    if not 'backurl' in data: 
        data['backurl'] = reverse('calendar_homepage')
    data['needquillinput'] = True
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
