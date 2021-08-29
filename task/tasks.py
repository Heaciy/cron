from celery import shared_task
import time


@shared_task
def add(x, y):
    print("任务函数add 正在执行...")
    time.sleep(2)
    return x + y
