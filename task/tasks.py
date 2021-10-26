from celery import shared_task
from django.contrib.auth.models import User
import time


@shared_task
def add(x, y, *args, **kwargs):
    print(kwargs)
    user = User.objects.get(id=kwargs.get('uid', 1))
    print(f"任务函数add 正在执行...\n用户{user.username}")
    time.sleep(2)
    return x + y


@shared_task
def generic(*args, **kwargs):
    print("generic task running...")
    print(f"args:\t{args}\nkwargs:\t{kwargs}")
