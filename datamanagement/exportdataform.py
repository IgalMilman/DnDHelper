import json
from datetime import datetime

import pytz
from django import forms
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from dndhelper import settings
from utils.widget import form_switch

from datamanagement import datagetters

EXPORT_FORMATS = [('json', 'json')]

class ExportDataForm(forms.Form):
    exportformat = forms.ChoiceField(label='Export format:', choices=EXPORT_FORMATS, initial='json', disabled=True)
    users = form_switch.SwitchOnOffField(label="Export users", required=False, initial=False)
    wiki = form_switch.SwitchOnOffField(label="Export Wiki", required=False, initial=True)

    @staticmethod
    def initializeData(request):
        if request.method == 'POST':
            form = ExportDataForm(request.POST)
        elif request.method == 'GET':
            form = ExportDataForm()
        else:
            return None
        data = {
        'action':'export',
        'PAGE_TITLE': 'Export data: ' + settings.SOFTWARE_NAME_SHORT,
        'minititle': 'Export Data',
        'submbutton': 'Export',
        'form': form,
        'built': datetime.now().strftime("%H:%M:%S"),
        'backurl': reverse('datamanagement_homepage'),
        #'newtab': True
        }
        return data

def exportData(form:ExportDataForm, request):
    if form is None:
        return None
    if not form.is_valid():
        return None
    export_format = 'json'
    if 'exportformat' in form.cleaned_data:
        export_format = form.cleaned_data['exportformat']
    result = {}
    if 'users' in form.cleaned_data:
        if form.cleaned_data['users']:
            result['users'] = datagetters.export_all_users(request.user)
    if 'wiki' in form.cleaned_data:
        if form.cleaned_data['wiki']:
            result['wiki'] = datagetters.export_all_wiki_pages(request.user)
    return result


def ExportDataFormParse(request):
    data= ExportDataForm.initializeData(request)
    if data is None:
        return redirect(reverse('datamanagement_homepage'))
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='export'):
            if data['form'].is_valid():
                export_data = exportData(data['form'], request)
                response = HttpResponse(json.dumps(export_data, indent=4, sort_keys=True), content_type='text/json')
                response['Content-Disposition'] = 'attachment; filename="'+ \
                    settings.SOFTWARE_NAME_SHORT+'_data'+datetime.today().strftime('%Y_%m_%d')+'.json"'
                return response
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
