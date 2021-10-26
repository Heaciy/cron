from task.utils import dumps_kwargs_safe, load_kwargs_from_str
from django.db import models
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask


@receiver(models.signals.post_save, sender=PeriodicTask)
def decorate_kwargs(sender, instance, **kwargs):
    """在创建、保存PeriodicTask时自动为其kwargs添加tid字段"""
    kwargs = load_kwargs_from_str(instance.kwargs)
    if not instance.name.startswith('celery.') and 'tid' not in kwargs:
        kwargs.update({'tid': instance.id})
        instance.kwargs = dumps_kwargs_safe(kwargs)
        instance.save()


@receiver(models.signals.post_delete, sender=PeriodicTask)
def clean_schedule(sender, instance, **kwargs):
    """删除PeriodicTask时自动清理相关联的schedule"""
    schedules = [instance.interval, instance.crontab,
                 instance.solar, instance.clocked]
    for schedule in schedules:
        if schedule and schedule.periodictask_set.all().count() == 0:
            schedule.delete()
