import uuid

from django.contrib.auth.models import User
from django.http import HttpRequest
from permissions import permissions_response

from wiki.permissionpage import PermissionPage
from wiki.permissionsection import PermissionSection
from wiki.wikipage import WikiPage
from wiki.wikisection import WikiSection


def get_sections(request:HttpRequest, wikipage: WikiPage) -> list:
    if wikipage is None:
        return None
    targetid = None
    if request.method == 'GET' and 'target' in request.GET:
        targetid = request.GET['target'] 
    if request.method == 'POST' and 'targetid' in request.POST:
        targetid = request.POST['targetid']
    if targetid is None:
        return None
    if targetid == 'all':
        result = wikipage.allpermissionable(request.user)
        if len(result)==0:
            return []
        else:
            return result 
    else:
        try:
            wikis = wikipage.wikisection_set.get(unid=uuid.UUID(targetid))
            if wikis is None:
                return None
            if wikis.permissionsable(request.user):
                return [wikis]
            return None
        except Exception:
            return None
    return None

def get_all_users_data()->list:
    allusers = []
    for user in  User.objects.all().order_by('first_name'):
        allusers.append(permissions_response.get_permission_data_empty(user))
    return allusers

def get_permissions_for_section(wikisection:WikiSection, allusers=None) -> list:
    if wikisection is None:
        return None
    if allusers is None:
        allusers = get_all_users_data()
    result = []
    processed_users = set()
    existintperms = wikisection.permissions.all()
    if not (existintperms is None): 
        for perm in existintperms:
            result.append(permissions_response.get_permission_data(perm))
            processed_users.add(perm.grantedto.get_full_name())
    for user in allusers:
        if not (user['grantedto']['fullname'] in processed_users):
            result.append(user)
    result = permissions_response.order_permission_data_list(result)
    result.insert(0, permissions_response.get_permission_data_empty(User(username='all', first_name='All')))
    return result

def get_wiki_page(request:HttpRequest, wikipageuuid:uuid.UUID) -> WikiPage:
    try:
        result = WikiPage.objects.get(unid=wikipageuuid)
        if result is None:
            return None
        return result
    except Exception:
        return None

def set_permissions_section(users:list, section:WikiSection, plevel:int, currentuser:User) -> int:
    if (users is None) or (section is None) or (currentuser is None):
        return -1
    if not section.permissionsable(currentuser):
        return -1
    result = 0
    for user in users:
        try:
            perm = PermissionSection.get(user, section, currentuser)
            if perm is None:
                pass
            perm.accesslevel = plevel
            perm.save()
            result = result + 1
        except Exception:
            pass
    return result

def get_users(request:HttpRequest)->list:
    if request.method=='POST' and 'username' in request.POST:
        if request.POST['username'] == 'all':
            return list(User.objects.all())
        else:
            try:
                user = User.objects.get(username = request.POST['username'])
                if user is None:
                    return None
                return [user]
            except:
                return None
    return None

def get_permissions_for_page(wikipage:WikiPage, allusers=None) -> list:
    if wikipage is None:
        return None
    if allusers is None:
        allusers = get_all_users_data()
    result = []
    processed_users = set()
    existintperms = wikipage.permissions.all()
    if not (existintperms is None): 
        for perm in existintperms:
            result.append(permissions_response.get_permission_data(perm))
            processed_users.add(perm.grantedto.get_full_name())
    for user in allusers:
        if not (user['grantedto']['fullname'] in processed_users):
            result.append(user)
    result = permissions_response.order_permission_data_list(result)
    result.insert(0, permissions_response.get_permission_data_empty(User(username='all', first_name='All')))
    return result

def get_permissions_data_section(sections:list) -> dict:
    if sections is None:
        return None
    result = {
        'permlevels': permissions_response.get_permission_level_data()
    }
    sectionsdata = []
    allusers = get_all_users_data()
    if len(sections)>1:
        result['page'] = get_permissions_for_page(sections[0].wikipage, allusers)
        sectionsdata.append({
            'secid': None,
            'sectitle': 'All',
            'secperm': get_permissions_for_section(WikiSection())
        })
    for section in sections:
        sectiondata = {
            'secid': section.unid,
            'sectitle': section.title,
            'secperm': get_permissions_for_section(section, allusers)
        }
        sectionsdata.append(sectiondata)
    result['sections'] = sectionsdata
    return result

def set_permissions_request_section(request:HttpRequest, sections:list) -> dict:
    try:
        if not ('permissionlevel' in request.POST):
            return None
        if sections is None:
            return None
        permlevel = int(request.POST['permissionlevel'])
        if not (isinstance(permlevel, int)):
            return None 
        users = get_users(request)
        if users is None:
            return None
        perm_count = 0
        for section in sections:
            perm_count = perm_count + set_permissions_section(users, section, permlevel, request.user)

        return {'status': 'success', 'countcreated': perm_count, 'countneeded':len(sections)*len(users) }
    except Exception as err:
        return None

def handle_permissions_request_section(request:HttpRequest, wikipage:WikiPage)->dict:
    sections = get_sections(request, wikipage)
    if sections is None:
        if request.method == 'POST':
            return handle_permissions_request_page(request, wikipage)
        return None
    if request.method == 'GET':
        return get_permissions_data_section(sections)
    if (request.method == 'POST') and ('action' in request.POST):
        if request.POST['action']=='setperm':
            return set_permissions_request_section(request, sections)
    return None

def set_permissions_page(users:list, page:WikiPage, plevel:int, currentuser:User) -> int:
    if (users is None) or (page is None) or (currentuser is None):
        return -1
    if not page.permissionsable(currentuser):
        return -1
    result = 0
    for user in users:
        try:
            perm = PermissionPage.get(user, page, currentuser)
            if perm is None:
                pass
            perm.accesslevel = plevel
            perm.save()
            result = result + 1
        except Exception:
            pass
    return result

def set_permissions_request_page(request:HttpRequest, page:WikiPage) -> dict:
    try:
        if not ('permissionlevel' in request.POST):
            return None
        if page is None:
            return None
        permlevel = int(request.POST['permissionlevel'])
        if not (isinstance(permlevel, int)):
            return None 
        users = get_users(request)
        if users is None:
            return None
        perm_count = set_permissions_page(users, page, permlevel, request.user)
        return {'status': 'success', 'countcreated': perm_count, 'countneeded':len(users) }
    except Exception as err:
        return None

def handle_permissions_request_page(request:HttpRequest, wikipage:WikiPage)->dict:
    if (request.method == 'POST') and ('action' in request.POST):
        if request.POST['action']=='setperm':
            return set_permissions_request_page(request, wikipage)
    return None
