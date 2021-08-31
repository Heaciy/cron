from django.contrib.auth.models import User
from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask
from django.contrib import admin
from .utils import load_from_kwargs


# TODO: 分别处理TaskResult和PeriodicTask的kwargs
# 从中解析出uid和tid再使用display和Concat组合进行排序
# https://docs.djangoproject.com/en/3.2/ref/models/database-functions/#concat
# https://docs.djangoproject.com/zh-hans/3.2/ref/contrib/admin/#django.contrib.admin.display
@property
@admin.display(description='owner')
def owner(self):
    uid = load_from_kwargs(self, 'uid')
    return User.objects.filter(id=int(uid)).first() if uid else None


@property
@admin.display(ordering='task_kwargs', description='task obj')
def task_obj(self):
    tid = load_from_kwargs(self, 'tid')
    return PeriodicTask.objects.filter(id=int(tid)).first() if tid else None


# 动态绑定
PeriodicTask.owner = owner
TaskResult.owner = owner
TaskResult.task_obj = task_obj
