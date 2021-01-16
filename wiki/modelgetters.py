import uuid

from wiki.models.wikipage import WikiPage


def form_all_wiki_pages_data(user):
    try:
        result = []
        wiki_pages = WikiPage.objects.all().order_by('-createdon')
        for wikip in wiki_pages:
            if (wikip.viewable(user)):
                result.append(wikip)
    except Exception as err:
        return None
    return {'wiki_pages': result}

def get_one_wiki_page_data(wikiuuid, user):
    try:
        wiki_page = WikiPage.objects.get(unid=wikiuuid)
        if (not wiki_page.viewable(user)):
            return None
        data={}
        data['wiki_page'] = wiki_page
        sections = wiki_page.allviewable(user)
        data['wiki_page_sections'] = sections
        return data
    except Exception as err:
        return None
