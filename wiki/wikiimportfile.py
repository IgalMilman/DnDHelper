import json
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from wiki.models.wikipage import WikiPage


class WikiImportForm(forms.Form):
    file = forms.FileField(label="Upload file to import", required=True)

def loadfile(file)->str:
    result = file.read()
    return result 

def WikiArticleFormParse(request) -> HttpResponse:
    data={}
    if not WikiPage.cancreate(request.user):
        return redirect(reverse('wiki_homepage'))
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='import'):
            form = WikiImportForm(request.POST, request.FILES)
            if form.is_valid():
                model = WikiPage.fromjson(json.loads(loadfile(request.FILES['file'])), commit = True)
                if model is not None:
                    messages.success(request, 'Page created successfully')
                    return redirect(model['page'].get_link())
            messages.error(request, 'The file was not a valid Wiki Article JSON object')
    else:
        form = WikiImportForm()
    data['action']='import'
    data['PAGE_TITLE'] = 'Import wiki article: ' + settings.SOFTWARE_NAME_SHORT
    data['minititle'] = 'Import Wiki Article'
    data['submbutton'] = 'Import'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    if not 'backurl' in data: 
        data['backurl'] = reverse('wiki_homepage')
    data['needquillinput'] = False
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
