import pdb
import time

from ratelimit.decorators import ratelimit
from user.utils import anonymous_required
from user.utils import send_captcha as _send_captcha
from user.forms import LoginForm, RegForm
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import render
from django.contrib import auth
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse
# Create your views here.


def logout(request):
    """退出"""
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('main')))


@anonymous_required
def login(request):
    """登陆"""
    # 使用ajax设置登陆cookie
    # 使用上下文管理
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('next', reverse('main')))
    else:
        login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'user/login.html', context)


@anonymous_required
def register(request):
    """用户注册"""
    if request.method == 'POST':
        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            print(dir(reg_form))
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            # pdb.set_trace()
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 删除验证码
            captcha_key = f'register:{email}'
            cache.delete_pattern(captcha_key)
            # 用户登录
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('next', reverse('main')))  # 返回主页
    else:
        reg_form = RegForm()
    context = {'reg_form': reg_form}
    return render(request, 'user/register.html', context)


@ratelimit(key='ip', rate='10/m')
def send_captcha(request):
    """发送验证码"""
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    last_time = request.GET.get('last_time', 0)
    interval = int(time.time())-last_time
    state = _send_captcha(email, send_for)
    if state and interval > 30:  # 2/m
        return JsonResponse({'state': 'success'})
    return JsonResponse({'state': 'failed'})
