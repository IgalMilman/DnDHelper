import collections
import copy
from datetime import datetime, timezone

from django import forms
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.urls import reverse
from dndhelper import views as main_views
from dndhelper.widget import quill

from wiki import wikipage, wikisection


class WikiSectionForm(forms.ModelForm):
    text = quill.QuillField(label='Text', widget=quill.QuillWidget({'toolbar': {'image': True, 'video': True}}))
    #file_field = forms.FileField(label="Attach files", widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    

    class Meta:
        model = wikisection.WikiSection
        fields = ('title', 'pageorder', 'text', )

    def save(self, commit=True):
        # TODO Download files from the Quil instead of writting them to the DB
        wikis = super(WikiSectionForm, self).save(commit=False)
        return wikis

    def get_files(self, request):
        return request.FILES.getlist('file_field')

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
                # files = form.get_files(request)
                # for f in files:
                #     uploaded_file.save_file_comment(model, f)
                return None
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'Add section: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Add Section'
                data['submbutton'] = 'Add section'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    cursection=wikisection.WikiSection.objects.get(unid=request.POST['targetid'])
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
                    cursection=wikisection.WikiSection.objects.get(unid=request.POST['targetid'])
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
                    cursection=wikisection.WikiSection.objects.get(unid=request.POST['targetid'])
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
        curpage = wikipage.WikiPage.objects.get(unid=wikipageuuid)
    except Exception as err:
        return redirect(reverse('wiki_homepage'))
    data = WikiSectionFormCreate(request, curpage)
    if data is None:
        return redirect(reverse('wiki_page', kwargs={'wikipageuuid': wikipageuuid}))
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
