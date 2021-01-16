import datetime

from django.conf import settings
from django.shortcuts import render


def notfound(request, data={}):
    data['PAGE_TITLE'] = 'Not found error: '+settings.SOFTWARE_NAME
    data['built'] = datetime.datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    return render(request, 'errors/notfound.html', data, content_type='text/html')


def view_404(request, exception):
    data = {}
    data['PAGE_TITLE'] = 'Not found error: '+settings.SOFTWARE_NAME
    data['built'] = datetime.datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = False
    return render(request, 'errors/notfound.html', data, content_type='text/html')
