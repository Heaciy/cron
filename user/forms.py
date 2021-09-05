from django import forms
from django.contrib import auth
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username',
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': 'Enter username or email'}))
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))

    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']
        user = auth.authenticate(
            username=username_or_email, password=password)  # 如果输入的是用户名
        if user is None:  # 该用户名“不存在”,在使用email测试是否存在
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(
                    email=username_or_email).username  # 通过email获取用户名
                user = auth.authenticate(username=username, password=password)
                if user is not None:  # 用户存在
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user  # 用户名存在
        return self.cleaned_data
