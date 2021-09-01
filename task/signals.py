from task.utils import dumps_kwargs_safe, load_kwargs_from_str
from django.db import models
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask


print("=========signal on task=========")


@receiver(models.signals.post_save, sender=PeriodicTask)
def decorate_kwargs(sender, instance, **kwargs):
    print(f"instance:{instance}")
    print(f"kwargs:{kwargs}")
    kwargs = load_kwargs_from_str(instance.kwargs)
    if 'tid' not in kwargs:
        kwargs.update({'tid': instance.id})
        instance.kwargs = dumps_kwargs_safe(kwargs)
        instance.save()
