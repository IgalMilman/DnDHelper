from django import forms
from dndhelper import views as main_views
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime
from wiki import wikipage
from dndhelper import settings
from dndhelper.widget import quill, form_switch
import pytz

class WikiPageForm(forms.ModelForm):
    text = quill.QuillField(label="Article text", widget=quill.QuillWidget({'toolbar': {'image': True, 'video': True}}), required=False)
    commonknowledge = form_switch.SwitchOnOffField(label="Is public knowledge?", required=False)
    class Meta:
        model = wikipage.WikiPage
        fields = ('title', 'commonknowledge', 'text', )
        # widgets = {
        #     'postedon':  forms.SplitDateTimeWidget
        # }

def WikiArticleFormParse(request):
    data={}
    data['PAGE_TITLE'] = 'Change posted atricle: ' + settings.SOFTWARE_NAME_SHORT
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            if not wikipage.WikiPage.cancreate(request.user):
                return redirect(reverse('wiki_homepage'))
            form = WikiPageForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.createdby = request.user
                model.updatedby = request.user
                model.save()
                return redirect(model.get_link())
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'Post an article: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Post Article'
                data['submbutton'] = 'Post article'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curpost=wikipage.WikiPage.objects.get(unid=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('wiki_homepage'))
                if not curpost.editable(request.user):
                    return redirect(reverse('wiki_homepage'))
                form = WikiPageForm(instance=curpost)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Post an article: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Change Posted Article'
                data['submbutton'] = 'Change posted article'
                data['backurl'] = curpost.get_link()
                data['deletebutton'] = 'Delete article'
            else:
                return redirect(reverse('wiki_homepage'))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curpost=wikipage.WikiPage.objects.get(unid=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('wiki_homepage'))
                if not curpost.editable(request.user):
                    return redirect(reverse('wiki_homepage'))
                form = WikiPageForm(request.POST, instance=curpost)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.updatedby = request.user
                    model.updatedon = datetime.now(pytz.utc)
                    model.save()
                    return redirect(model.get_link())                    
                curpost.createdon = datetime.now(pytz.utc)
                curpost.save()
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['PAGE_TITLE'] = 'Post an article: ' + settings.SOFTWARE_NAME_SHORT
                data['minititle'] = 'Change Posted Article'
                data['submbutton'] = 'Change posted article'
                data['backurl'] = curpost.get_link()
                data['deletebutton'] = 'Delete article'
            else:
                return redirect(reverse('wiki_homepage'))
        elif (request.POST['action']=='delete'): 
            if('targetid' in request.POST):
                try:
                    curpost=wikipage.WikiPage.objects.get(unid=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('wiki_homepage'))
                if not curpost.editable(request.user):
                    return redirect(reverse('wiki_homepage'))
                curpost.delete()
                return redirect(reverse('wiki_homepage'))
            else:
                return redirect(reverse('wiki_homepage'))
        else:
            return redirect(reverse('wiki_homepage'))
    else:
        if not wikipage.WikiPage.cancreate(request.user):
            return redirect(reverse('wiki_homepage'))
        form = WikiPageForm()
        data['action']='add'
        data['PAGE_TITLE'] = 'Post an article: ' + settings.SOFTWARE_NAME_SHORT
        data['minititle'] = 'Post Article'
        data['submbutton'] = 'Post article'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    if not 'backurl' in data: 
        data['backurl'] = reverse('wiki_homepage')
    data['needquillinput'] = True
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')