import uuid

from django.contrib.auth.models import User
from django.http import HttpRequest
from permissions import permissions_response

from customcalendar.models.calendarevent import CEvent
from customcalendar.models.permissionevent import PermissionCEvent


def get_event(request:HttpRequest, eventuuid:uuid.UUID) -> CEvent:
    try:
        result = CEvent.objects.get(unid=eventuuid)
        if result is None:
            return None
        return result
    except Exception:
        return None

def get_all_users_data()->list:
    allusers = []
    for user in  User.objects.all().order_by('first_name'):
        allusers.append(permissions_response.get_permission_data_empty(user))
    return allusers

def get_permissions_for_event(event:CEvent, allusers=None) -> list:
    if event is None:
        return None
    if allusers is None:
        allusers = get_all_users_data()
    result = []
    processed_users = set()
    existintperms = event.permissions.all()
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

def get_permissions_data_event(event:CEvent) -> dict:
    if event is None:
        return None
    result = {
        'permlevels': permissions_response.get_permission_level_data()
    }
    sectionsdata = []
    allusers = get_all_users_data()
    sectiondata = {
        'secid': None,
        'sectitle': event.title,
        'secperm': get_permissions_for_event(event, allusers)
    }
    sectionsdata.append(sectiondata)
    result['sections'] = sectionsdata
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

def set_permissions_event(users:list, event:CEvent, plevel:int, currentuser:User) -> int:
    if (users is None) or (event is None) or (currentuser is None):
        return -1
    if not event.permissionsable(currentuser):
        return -1
    result = 0
    for user in users:
        try:
            perm = PermissionCEvent.get(user, event, currentuser)
            if perm is None:
                pass
            perm.accesslevel = plevel
            perm.save()
            result = result + 1
        except Exception:
            pass
    return result

def set_permissions_request_event(request:HttpRequest, event:CEvent) -> dict:
    try:
        if not ('permissionlevel' in request.POST):
            return None
        if event is None:
            return None
        permlevel = int(request.POST['permissionlevel'])
        if not (isinstance(permlevel, int)):
            return None 
        users = get_users(request)
        if users is None:
            return None
        perm_count = set_permissions_event(users, event, permlevel, request.user)
        return {'status': 'success', 'countcreated': perm_count, 'countneeded':len(users) }
    except Exception as err:
        return None

def handle_permissions_request_event(request:HttpRequest, event:CEvent)->dict:
    if request.method == 'GET':
        return get_permissions_data_event(event)
    if (request.method == 'POST') and ('action' in request.POST):
        if request.POST['action']=='setperm':
            return set_permissions_request_event(request, event)
    return None