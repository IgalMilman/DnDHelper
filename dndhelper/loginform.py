from django.conf import settings
from django.shortcuts import reverse
from django.contrib.auth import forms as auth_forms


class MyAuthLoginForm(auth_forms.AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(MyAuthLoginForm, self).__init__(*args, **kwargs)


class my_reset_password_form(auth_forms.PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super(my_reset_password_form, self).__init__(*args, **kwargs)