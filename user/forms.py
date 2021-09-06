from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.cache import cache


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


# 注册表单
class RegForm(forms.Form):
    username = forms.CharField(
        label='Username', max_length=30, min_length=4,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter username'}))
    email = forms.EmailField(
        label='email',
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter E-mail'})
    )
    password = forms.CharField(
        label='password', max_length=30, min_length=6,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    password_confirm = forms.CharField(
        label='password confirm', max_length=30, min_length=6,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter password again'})
    )
    verification_code = forms.CharField(
        label='PIN',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter The PIN'})
    )

    # 钩子函数,在views.py中验证表单数据调用is_valid()时,该函数会调用clean和clean_xxx方法
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已注册')
        return email

    def clean_password_confirm(self):
        password = self.cleaned_data['password']
        password_confirm = self.cleaned_data['password_confirm']
        if password != password_confirm:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_confirm

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get(
            'verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        captcha_key = f'register:{self.clean_email()}'
        print(f'captcha key:{captcha_key}')
        if not (cache.has_key(captcha_key) and verification_code == cache.get(captcha_key)):
            raise forms.ValidationError('验证码错误')
        return verification_code
