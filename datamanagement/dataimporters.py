from datetime import datetime

from dateutil import parser
from django.contrib.auth.models import User
from wiki import wikipage


def import_all_wikipages(wikipagelist:list, override:bool=True)->list:
    try:
        if wikipagelist is None:
            return None
        result = []
        for page in wikipagelist:
            try:
                p = wikipage.WikiPage.fromjson(page, commit=True, override=override)
                if p is not None:
                    result.append(p)
            except Exception:
                pass
        return result
    except Exception:
        return None


def user_from_json(userdict:dict, commit:bool = False, override:bool = True)->User:
    if userdict is None:
        return None
    if 'username' in userdict:
        username = userdict['username']
    else:
        return None
    if 'email' in userdict:
        email = userdict['email']
    else:
        return None
    if 'issuper' in userdict:
        try:
            issuper = bool(userdict['issuper'])
        except Exception:
            issuper = False
    else:
        issuper=False
    if 'active' in userdict:
        try:
            active = bool(userdict['active'])
        except Exception:
            active = True
    else:
        active = True
    if 'staff' in userdict:
        try:
            staff = bool(userdict['staff'])
        except Exception:
            staff = True
    else:
        staff = True
    if 'ph' in userdict:
        ph = userdict['ph']
    else:
        ph=''
    if 'firstname' in userdict:
        firstname = userdict['firstname']
    else:
        firstname=''
    if 'lastname' in userdict:
        lastname = userdict['lastname']
    else:
        lastname=''
    if 'datejoined' in userdict:
        datejoined = parser.parse(userdict['datejoined'])
    else:
        datejoined=datetime.now()
    try:
        user = User.objects.get_or_create(username=username)
        user.email=email
        user.is_active=active
        user.is_staff=staff
        user.first_name=firstname
        user.last_name=lastname
        user.date_joined=datejoined
        if commit:
            user.save()
        return user
    except Exception:
        return None


def import_all_users(userslist:list) -> list:
    try:
        if userslist is None:
            return None
        result = []
        for udict in userslist:
            try:
                u = user_from_json(udict, commit=True)
                if u is not None:
                    result.append(u)
            except Exception:
                pass
        return result
    except Exception:
        return None
