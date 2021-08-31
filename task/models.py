from django.db import models
from django.contrib.auth.models import User
from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask
from .utils import load_from_kwargs


# class ExtraTaskResultInfo(models.Model):
#     task_result = models.OneToOneField(TaskResult, on_delete=models.CASCADE)
#     task_creator = models.ForeignKey(User, on_delete=models.CASCADE)

# class ExtraTaskBeatInfo(models.Model):
#     task_beat = models.OneToOneField(PeriodicTask,on_delete=models.CASCADE)
#     task_creator = models.ForeignKey(User, on_delete=models.CASCADE)

@property
def owner(self):
    uid = load_from_kwargs(self, 'uid')
    return User.objects.filter(id=int(uid)).first() if uid else None


@property
def task_obj(self):
    tid = load_from_kwargs(self, 'tid')
    return PeriodicTask.objects.filter(id=int(tid)).first() if tid else None

# 动态绑定
PeriodicTask.owner = owner
TaskResult.owner = owner
TaskResult.task_obj = task_obj
