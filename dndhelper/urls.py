"""dndhelper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import handler404
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import reverse
from django.urls import include, path, re_path, reverse_lazy

from dndhelper import error_views as error_views
from dndhelper import loginform as dndhelper_loginform
from dndhelper import views as dndhelper_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dndhelper_views.homepage, name='admin'),
    path('', dndhelper_views.homepage, name='homepage'),
    path('wiki/', include('wiki.urls')),
    path('', dndhelper_views.homepage, name=''),
    path('me', dndhelper_views.userpersonalpage, name='personal_page'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(form_class=dndhelper_loginform.my_reset_password_form, 
    html_email_template_name='registration/forgot_password.htm'), 
    {'password_reset_form':dndhelper_loginform.my_reset_password_form, 
    'form_class': dndhelper_loginform.my_reset_password_form}, 'password_reset'),
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=dndhelper_loginform.MyAuthLoginForm), name='login'),
    path('accounts/register/', dndhelper_views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('data/', include('datamanagement.urls')),
]

#handler404 = error_views.view_404 
