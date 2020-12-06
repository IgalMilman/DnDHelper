"""Wiki URL Configuration

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
from django.urls import include, path, re_path, reverse_lazy

from wiki import views as wiki_views

urlpatterns = [
    path('<uuid:wikipageuuid>', wiki_views.wikiPageOpen, name='wiki_page'),
    path('', wiki_views.wikiHomePage, name='wiki_homepage'),
    path('<uuid:wikipageuuid>/edit', wiki_views.wikiAddSectionToWikiPageFormSubmit, name='wiki_page_add_section'),
    path('import', wiki_views.wikiImportOnePage, name='wiki_import'),
    path('edit', wiki_views.wikiPageForm, name='wiki_new_page'),
    path('<uuid:wikipageuuid>/perm', wiki_views.wikiPermissionsAjaxRequestHandle, name='wiki_page_perm'),
    path('<uuid:wikipageuuid>/export', wiki_views.wikiExportOnePage, name='wiki_page_export'),
    path('export/all', wiki_views.wikiExportAllPages, name='wiki_export_all')
]
