from django.contrib.auth.models import User
from wiki.models.wikipage import WikiPage


def export_all_wiki_pages(user):
    try:
        result = []
        for page in WikiPage.objects.all():
            try:
                result.append(page.json())
            except Exception:
                pass
        return result
    except Exception:
        return None


def user_to_json(user:User)->dict:
    if user is None:
        return None
    return {
        'username': user.get_username(),
        'issuper': user.is_superuser,
        'active': user.is_active,
        'staff': user.is_staff,
        'ph': user.password,
        'email': user.email,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'datejoined': user.date_joined.isoformat()
    }


def export_all_users(user):
    try:
        result = []
        for u in User.objects.all():
            try:
                result.append(user_to_json(u))
            except Exception:
                pass
        return result
    except Exception:
        return None
