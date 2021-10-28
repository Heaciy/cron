import random
import re
import string
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail


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


# 预编译re以节省时间 / 放到设置里
username_rec = re.compile(r'^[A-Za-z]{1}[A-Za-z0-9_-]{3,15}$')
email_rec = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


def username_available(username):
    """判断用户名是否满足/未注册"""
    if username_rec.match(username):
        if User.objects.filter(username=username).exists():
            return True
    return False


def email_available(email):
    """判断邮件是否合法/未注册"""
    if email_rec.match(email):
        if User.objects.filter(username=email).exists():
            return True
    return False


def send_captcha(email, send_for):
    """发送给验证码"""
    send_for_options = {'register': 'Verify register',
                        'bind_email': 'Bind email', 'reset_password': 'Reset password'}
    if email_rec.match(email) and send_for in send_for_options:
        subject = send_for_options.get(send_for)
        code = ''.join(random.sample(
            string.ascii_letters + string.digits, 6)).lower()
        print(f'captcha keys:{send_for}:{email}')
        cache.set(f'{send_for}:{email}', code, timeout=30 * 60)
        send_mail(
            subject,
            f'captcha: {code}, valid for 30 minutes',
            'Heaciy <' + settings.EMAIL_HOST_USER + '>',
            [email],
            fail_silently=False,
        )
        return True
    return False
