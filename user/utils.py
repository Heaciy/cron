from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def anonymous_required(function=None, redirect_url=None):
    """限制登陆后的用户不能访问"""
    if not redirect_url:
        redirect_url = settings.MAIN_URL

    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )

    if function:
        return actual_decorator(function)
    return actual_decorator
