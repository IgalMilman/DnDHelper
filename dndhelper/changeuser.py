from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, reverse


class ChangeUserForm(auth_forms.UserChangeForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:            
            print(kwargs['instance'].first_name)
            self.fields['first_name'].initial = kwargs['instance'].first_name
            self.fields['last_name'].initial = kwargs['instance'].last_name

    def save(self, commit=True):
        self.instance.first_name = self.cleaned_data["first_name"]
        self.instance.last_name = self.cleaned_data["last_name"]
        self.instance.email = self.cleaned_data["email"]
        if commit:
            self.instance.save()
        return self.instance

def changeUserFormParser(request):
    data={}
    data['PAGE_TITLE'] = 'Change user: ' + settings.SOFTWARE_NAME_SHORT
    data['action']='change'
    if not 'backurl' in data: 
        data['backurl'] = reverse('personal_page')
    data['needquillinput'] = True
    if request.method == 'POST':
        form = ChangeUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Changes were saved successfully')
            return redirect(reverse('personal_page'))
    else:
        form = ChangeUserForm(instance=request.user)
    data['PAGE_TITLE'] = 'Change user: ' + settings.SOFTWARE_NAME_SHORT
    data['minititle'] = 'Change your account'
    data['submbutton'] = 'Save'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 

    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
