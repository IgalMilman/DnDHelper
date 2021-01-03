import logging
from datetime import datetime

import pytz
from customcalendar.models.calendarsettings import CCalendar 
from django import forms


class CurDateForm(forms.ModelForm):
    class Meta:
        model = CCalendar
        fields = ('currentday', 'currentmonth', 'currentyear', )

def CurDateFormParser(request):
    if not CCalendar.canedit(request.user):
        return {'status': 'failed', 'message': 'No permissions to edit'}
    if (request.method != 'POST') or not ('action' in request.POST):
        return {'status': 'failed', 'message': 'Wrong request.'}
    if (request.POST['action']=='changed'):
        if('targetid' in request.POST):
            try:
                curcalendar=CCalendar.objects.get(id=request.POST['targetid'])
            except Exception as e:
                logging.error(e)
            if curcalendar is not None:
                try:
                    form = CurDateForm(request.POST, instance=curcalendar)
                    model = form.save(commit=False)
                    model.save()
                    return {'status': 'success', 'message': 'Data saved'}
                except Exception as e:
                    logging.error(e)
    return {'status': 'failed', 'message': 'Failed to save the data'}
