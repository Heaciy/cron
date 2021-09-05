from django.shortcuts import render
from django.contrib import auth
from django.shortcuts import redirect
from django.urls import reverse
# Create your views here.


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('main')))


def login(request):
    # 使用ajax设置登陆cookie
    # 使用上下文管理
    if request.method == 'GET':
        return render(request,'user/login.html')
