import json
import logging
import os
from datetime import datetime
from mimetypes import guess_type

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.utils.encoding import smart_str
from dndhelper import views as main_views

from wiki import (modelgetters, wikiimportfile, wikipageform,
                  wikipermissionsresponse, wikisectionform)
from wiki.wikipage import WikiPage
from wiki.wikisection import WikiSection

# Create your views here.


@login_required( login_url = 'login' )
def wikiPageOpen(request, wikipageuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    datawikipage = modelgetters.get_one_wiki_page_data(wikipageuuid, request.user)
    if datawikipage is None:
        return redirect(reverse('wiki_homepage'))
    data_section_form = wikisectionform.WikiSectionFormCreate(request, datawikipage['wiki_page'])
    if data_section_form is None:
        data = datawikipage
    else:
        data = {**data_section_form, **datawikipage}
    data['PAGE_TITLE'] = 'Wiki: '+settings.SOFTWARE_NAME_SHORT
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    data['needquillinput'] = True
    return render(request, 'views/wikipage.html', data, content_type='text/html')

@login_required( login_url = 'login' )
def wikiPageForm(request):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    return wikipageform.WikiArticleFormParse(request)

@login_required( login_url = 'login' )
def wikiAddSectionToWikiPageFormSubmit(request, wikipageuuid):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    return wikisectionform.WikiSectionFormParse(request, wikipageuuid)

@login_required( login_url = 'login' )
def wikiChangeSectionToWikiPageFormSubmit(request, wikipageuuid):    
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    return wikisectionform.WikiSectionFormParse(request, wikipageuuid)

@login_required( login_url = 'login' )
def wikiHomePage(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    data = modelgetters.form_all_wiki_pages_data(request.user)         
    data['add_wiki_pages'] = WikiPage.cancreate(request.user)
    data['PAGE_TITLE'] = 'Wiki: ' + settings.SOFTWARE_NAME_SHORT
    data['built'] = datetime.now().strftime("%H:%M:%S")
    data['needdatatables'] = True
    data['needquillinput'] = False
    return render(request, 'views/allwiki.html', data, content_type='text/html')

@login_required( login_url = 'login' )
def wikiPermissionsAjaxRequestHandle(request, wikipageuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    wikipage = wikipermissionsresponse.get_wiki_page(request, wikipageuuid)
    if wikipage is None:
        return JsonResponse({'status': 'failed', 'message': 'wiki page not found'}, status=404, safe=False)
    data = wikipermissionsresponse.handle_permissions_request(request, wikipage)
    if data is None:
        return JsonResponse({'status': 'failed', 'message': 'error in the query'}, status=406, safe=False)
    return JsonResponse(data, status=200, safe=False)

@login_required( login_url = 'login' )
def wikiExportOnePage(request, wikipageuuid):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    wikipage = wikipermissionsresponse.get_wiki_page(request, wikipageuuid)
    if (wikipage is None) or (not wikipage.editable(request.user)) :
        return redirect(reverse('wiki_homepage'))
    wikijson = wikipage.json()
    response = HttpResponse(json.dumps(wikijson, indent=4, sort_keys=True), content_type='text/json')
    response['Content-Disposition'] = 'attachment; filename="wiki_page.json"'
    return response

@login_required( login_url = 'login' )
def wikiImportOnePage(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    return wikiimportfile.WikiArticleFormParse(request)

@login_required( login_url = 'login' )
def wikiExportAllPages(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    all_wiki_json = modelgetters.export_all_wiki_pages(request.user)
    response = HttpResponse(json.dumps(all_wiki_json, indent=4, sort_keys=True), content_type='text/json')
    response['Content-Disposition'] = 'attachment; filename="all_wiki_pages.json"'
    return response

@login_required( login_url = 'login' )
def wikiImportAllPages(request):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    all_wiki_json = modelgetters.export_all_wiki_pages(request.user)
    response = HttpResponse(json.dumps(all_wiki_json, indent=4, sort_keys=True), content_type='text/json')
    response['Content-Disposition'] = 'attachment; filename="all_wiki_pages.json"'
    return response


@login_required( login_url = 'login' )
def wikiPageFile(request, wikipageuuid, filename):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    try:
        wikipage = WikiPage.objects.get(unid=wikipageuuid)
    except Exception:
        wikipage = None
    if wikipage is None:
        return HttpResponseNotFound("File was not found")
    filecontent = wikipage.get_file(filename)
    if filecontent is None:
        return HttpResponseNotFound("File was not found")
    response = HttpResponse(filecontent, content_type=guess_type(filename)[0])
    #response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)
    #response['X-Sendfile'] = smart_str(filename)
    return response


@login_required( login_url = 'login' )
def wikiSectionFile(request, wikipageuuid, wikisectionuuid, filename):
    valid, response = main_views.initRequest(request)
    if not valid:
        return response
    try:
        wikisection = WikiSection.objects.get(unid=wikisectionuuid)
    except Exception:
        wikisection = None
    if wikisection is None:
        return HttpResponseNotFound("File was not found")
    filecontent = wikisection.get_file(filename)
    if filecontent is None:
        return HttpResponseNotFound("File was not found")
    response = HttpResponse(filecontent, content_type=guess_type(filename)[0])
    #response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)
    #response['X-Sendfile'] = smart_str(filename)
    return response

