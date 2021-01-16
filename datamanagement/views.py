import json
import logging
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, reverse
from utils.usefull_functions import initRequest

from datamanagement import datagetters, exportdataform, importdataform

# Create your views here.

@login_required( login_url = 'login' )
def dataHomePage(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    data = {}
    data['PAGE_TITLE'] = 'Data management: ' + settings.SOFTWARE_NAME
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    return render(request, 'datamanagement/views/datamanagement_homepage.html', data, content_type='text/html')
    

@login_required( login_url = 'login' )
def dataExportAllData(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    return exportdataform.ExportDataFormParse(request)

@login_required( login_url = 'login' )
def dataImportAllData(request):
    valid, response = initRequest(request)
    if not valid:
        return response
    return importdataform.ImportDataFormParse(request)


