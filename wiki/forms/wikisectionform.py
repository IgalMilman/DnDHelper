import collections
import copy
from datetime import datetime, timezone

from django import forms
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.urls import reverse
from utils.widget import form_switch, quill

from wiki.models.wikipage import WikiPage
from wiki.models.wikisection import WikiSection


class WikiSectionForm(forms.ModelForm):
    text = quill.QuillField(label='Text', widget=quill.QuillWidget({'toolbar': {'image': True, 'video': True}}))
    commonknowledge = form_switch.SwitchOnOffField(label="Is public knowledge?", required=False)
    

    class Meta:
        model = WikiSection
        fields = ('title', 'pageorder', 'commonknowledge', 'text', )

    def save(self, commit=True):
        wikis = super(WikiSectionForm, self).save(commit=False)
        return wikis

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:            
            self.fields['text'].widget.quillobject = kwargs['instance']


def WikiSectionFormCreate(request, curpage):
    data={}
    if curpage is None:
        return None
    data['PAGE_TITLE'] = 'Change section: ' + settings.SOFTWARE_NAME_SHORT
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            if not curpage.editable(request.user):
                return None
            form = WikiSectionForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.wikipage = curpage
                model.createdby = request.user
                model.updatedby = request.user
                model.save()
                return None
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'Add section: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Add Section'
                data['submbutton'] = 'Add section'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    cursection=WikiSection.objects.get(unid=request.POST['targetid'])
                except Exception:
                    return None
                if not cursection.editable(request.user):
                    return None
                form = WikiSectionForm(instance=cursection)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['edittargetsection'] = cursection
                data['PAGE_TITLE'] = 'Change section: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Change Section'
                data['submbutton'] = 'Change section'
                data['deletebutton'] = 'Delete section'
            else:
                return None
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    cursection=WikiSection.objects.get(unid=request.POST['targetid'])
                except Exception:
                    return None
                if not cursection.editable(request.user):
                    return None
                form = WikiSectionForm(request.POST, instance=cursection)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.updatedon = datetime.now(timezone.utc)
                    model.updatedby = request.user
                    model.save()
                    return None
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['edittargetsection'] = cursection
                data['PAGE_TITLE'] = 'Change section: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Change Section'
                data['submbutton'] = 'Change section'
                data['deletebutton'] = 'Delete section'
            else:
                return None
        elif (request.POST['action']=='delete'):
            if('targetid' in request.POST):
                try:
                    cursection=WikiSection.objects.get(unid=request.POST['targetid'])
                except Exception:
                    return None
                if not cursection.editable(request.user):
                    return None
                cursection.delete()
                return None
            else:
                return None
    else:
        if not curpage.editable(request.user):
            return None
        form = WikiSectionForm()
        form.fields['commonknowledge'].initial = curpage.commonknowledge
        data['action']='add'
        data['PAGE_TITLE'] = 'Add section: ' + settings.SOFTWARE_NAME_SHORT
        data['minititle'] = 'Add Section'
        data['submbutton'] = 'Add section'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['needquillinput'] = True
    data['backurl'] = reverse('wiki_page', kwargs={'wikipageuuid': curpage.unid})
    return data

def WikiSectionFormParse(request, wikipageuuid):
    try:
        curpage = WikiPage.objects.get(unid=wikipageuuid)
    except Exception as err:
        return redirect(reverse('wiki_homepage'))
    data = WikiSectionFormCreate(request, curpage)
    if data is None:
        return redirect(reverse('wiki_page', kwargs={'wikipageuuid': wikipageuuid}))
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
