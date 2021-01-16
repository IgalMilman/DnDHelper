from crum import get_current_user


def is_module_accessible(user=None):
    if user is None:
        user = get_current_user()
    if user is None:
        return False
    return user.is_superuser
