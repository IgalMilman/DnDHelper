import json
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from utils.widget import form_switch

from datamanagement import dataimporters


class ImportDataForm(forms.Form):
    override = form_switch.SwitchOnOffField(label="Override data", required=False, initial=False)
    file = forms.FileField(label="Upload file to import", required=True)

def loadfile(file)->str:
    result = file.read()
    return result 

def ImportDataFormParse(request) -> HttpResponse:
    data={}
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='import'):
            form = ImportDataForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    inputdict = json.loads(loadfile(request.FILES['file']))
                    override = form.cleaned_data['override']
                    if 'users' in inputdict:
                        users = dataimporters.import_all_users(inputdict['users'])
                        if users is not None:
                            messages.success(request, 'Imported {0} users to the system'.format(len(users)))
                    if 'wiki' in inputdict:
                        wiki = dataimporters.import_all_wikipages(inputdict['wiki'], override=override)
                        if wiki is not None:
                            messages.success(request, 'Imported {0} wiki pages to the system'.format(len(wiki)))
                    return redirect(reverse('datamanagement_homepage'))
                except Exception as ex:
                    pass
            messages.error(request, 'The file was not a valid data file')
    else:
        form = ImportDataForm()
    data['action']='import'
    data['PAGE_TITLE'] = 'Import data: ' + settings.SOFTWARE_NAME_SHORT
    data['minititle'] = 'Import Data'
    data['submbutton'] = 'Import'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    if not 'backurl' in data: 
        data['backurl'] = reverse('datamanagement_homepage')
    data['needquillinput'] = False
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
