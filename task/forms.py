from os import WEXITED
from django import forms

class DailyCPTaskForm(forms.Form):
    username = forms.CharField(label='学号',max_length=20,widget=forms.TextInput)
    password = forms.CharField(label='密码',max_length=20,widget=forms.PasswordInput)
    crontab = forms.CharField(label='时间',max_length=20,widget=forms.TextInput)
    