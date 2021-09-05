from user.utils import anonymous_required
from user.forms import LoginForm
from django.shortcuts import render
from django.contrib import auth
from django.shortcuts import redirect
from django.urls import reverse
# Create your views here.


def logout(request):
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
            return redirect(request.GET.get('from', reverse('main')))  # 返回到home界面，'home与urls.py中的name对应'
            # 返回到user_info界面
            # TODO(Heaciy): 把from改成next？
            # return redirect(request.GET.get('from', request.GET.get('next', reverse('user_info', kwargs={
            #     'username': user.username}))))
            # return redirect(request.GET.get('from', reverse('user_info', kwargs={'username': user.username})))
    else:
        login_form = LoginForm()
    context = {'login_form': login_form}
    return render(request, 'user/login.html', context)

def register(request):
    if request.method == 'GET':
        return render(request, 'user/register.html')
