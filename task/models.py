from django.db import models
from django.contrib.auth.models import Group, User
from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


#TODO: limit/available
class AvlTask(models.Model):
    name = models.CharField(
        max_length=20, verbose_name=_('name'), unique=True
    )
    task = models.CharField(
        max_length=100, verbose_name=_('task'), unique=True)
    groups = models.ManyToManyField(
        Group, verbose_name=_('groups'), blank=True)
    description = models.TextField(verbose_name=_('description'))

    class Meta:
        verbose_name = _('available task')
        verbose_name_plural = _('available tasks')

    def __str__(self) -> str:
        return f"AvlTask: {self.task}"

    def avl_for(self, user: User):
        return True

    @classmethod
    def avl_tasks(cls):
        return [task[0] for task in cls.objects.values_list("task")]


# TODO: 分别处理TaskResult和PeriodicTask的kwargs
# 从中解析出uid和tid再使用display和Concat组合进行排序
# https://docs.djangoproject.com/en/3.2/ref/models/database-functions/#concat
# https://docs.djangoproject.com/zh-hans/3.2/ref/contrib/admin/#django.contrib.admin.display


from .utils import load_from_kwargs
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
