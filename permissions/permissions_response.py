import json

from django.contrib.auth.models import User

from permissions.models.permissions import (PERMISSION_LEVELS_DICTIONARY,
                                            PERMISSION_LEVELS_TUPLES,
                                            Permission)


def get_permission_level_data() -> list:
    return list(PERMISSION_LEVELS_TUPLES)

def user_to_dictionary(user:User) -> dict:
    if user is None:
        return None
    result = {
        'username': user.get_username(),
        'fullname': user.get_full_name(),
        'issup': user.is_superuser,
    }
    return result

def get_permission_data(perm:Permission) -> dict:
    result = {
        'createdon': perm.createdon,
        'createdby': user_to_dictionary(perm.createdby),
        'grantedto': user_to_dictionary(perm.grantedto),
        'permlevel': perm.accesslevel,
    }
    return result

def get_permission_data_empty(user:User) -> dict:
    result = {
        'createdon': None,
        'createdby': None,
        'grantedto': user_to_dictionary(user),
        'permlevel': PERMISSION_LEVELS_TUPLES[0][0],
    }
    return result

def order_permission_data_list(permdata: list) -> list:
    if (permdata is None):
        return None
    permdata.sort(key=lambda x: x['grantedto']['fullname'], reverse=False)
    return permdata

def parse_perm_data(permdict: dict) -> dict:
    result = {}
    if 'grantedto' in result:
        try:
            if 'all'==permdict['grantedto']:
                target = list(User.objects.all())
            else:
                target = User.objects.get(username=permdict['grantedto'])
            if target is None:
                return None
            result['target'] = target
        except:
            return None
    else:
        return None
    if 'permlevel' in result:
        permlevel = PERMISSION_LEVELS_TUPLES[0][0]
        for plevels in PERMISSION_LEVELS_TUPLES:
            if plevels[0] <= result['permlevel']:
                permlevel = plevels[0]
            else:
                break
        result['permlevel']
    else:
        result['permlevel'] = 0
    return result
    