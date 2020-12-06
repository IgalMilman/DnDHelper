from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, reverse


class RegistrationForm(auth_forms.UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username")

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

def register(request):
    data={}
    data['PAGE_TITLE'] = 'Register: ' + settings.SOFTWARE_NAME_SHORT
    data['action']='register'
    if not 'backurl' in data: 
        data['backurl'] = reverse('wiki_homepage')
    data['needquillinput'] = True
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect(reverse('login'))
    else:
        form = RegistrationForm()
    data['PAGE_TITLE'] = 'Register: ' + settings.SOFTWARE_NAME_SHORT
    data['minititle'] = 'Register an account'
    data['submbutton'] = 'Register'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 

    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
