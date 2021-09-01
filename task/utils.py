from datetime import datetime
import json
from typing import Dict, List
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_celery_results.models import TaskResult
from celery.exceptions import NotRegistered
from cron import celery_app


def add_interval_schedule(every, period):
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=every, period=period)
    return schedule


def delete_interval_schedule(schedule_id):
    schedule = IntervalSchedule.objects.get(id=schedule_id)
    # 反向查询，如果无关联task则删除，否则不删除
    if schedule.periodictask_set.all().count() == 0:
        schedule.delete()


def add_periodic_task_by_interval(interval_id, name, task):
    tasks = list(sorted(name for name in celery_app.tasks
                        if not name.startswith('celery.')))
    if task not in tasks:
        raise NotRegistered(f"Task {task} was not registed")

    interval_obj = IntervalSchedule.objects.get(id=interval_id)
    periodic_task, created = PeriodicTask.objects.get_or_create(
        interval=interval_obj,
        name=name,
        task=task
    )


def disable_periodic_task():
    pass


def enable_periodic_task():
    pass


def load_from_kwargs(obj, key):
    """使用getattr同时适配TaskResult和PeriodicTask"""
    kwargs_str = getattr(obj, "task_kwargs") if hasattr(obj, "task_kwargs")\
        else getattr(obj, "kwargs")
    kwargs = json.loads(kwargs_str.strip("\"").replace('\'', '\"'))
    return kwargs.get(key, None)


def load_kwargs_from_str(str):
    """将kwargs的str转化为json对象"""
    kwargs = json.loads(str.strip("\"").replace('\'', '\"'))
    return kwargs

def load_kwargs_from_str_safe(str):
    """去除kwargs中的uid和tid"""
    kwargs = load_kwargs_from_str(str)
    if 'uid' in kwargs:
        del kwargs['uid']
    if 'tid' in kwargs:
        del kwargs['tid']
    return kwargs

def load_args_from_str(str):
    """将args的str转化为json对象"""
    args = json.loads(str.strip("\"").replace('\'', '\"'))
    return args


def load_strftime_from_datetime(date_time):
    """将datetime转换为strftime"""
    return datetime.strftime(date_time, '%Y-%m-%d %H:%M:%S')


def serialize_result(results: List[TaskResult]) -> List[Dict]:
    """手动序列化result"""
    data = [{'task_name': result.task_name,
             'task_obj': str(result.task_obj),
             'task_owner': str(result.owner),
             'task_args': load_args_from_str(result.task_args),
             'task_kwargs': load_kwargs_from_str_safe(result.task_kwargs),
             'status': result.status,
             'result': result.result,
             'date_done': load_strftime_from_datetime(result.date_done)
             }
            for result in results]
    return data


def serialize_task(tasks: List[PeriodicTask]) -> List[Dict]:
    """手动序列化task"""
    data = [{
        'name': task.name,
        'task': task.task,
        'owner': str(task.owner),
        'interval': str(task.interval),
        'crontab': str(task.crontab),
        'args': load_args_from_str(task.args),
        'kwargs': load_kwargs_from_str_safe(task.kwargs),
        'enabled': str(task.enabled),
        'total_run_count': task.total_run_count,
        'date_changed': load_strftime_from_datetime(task.date_changed),
        'description': task.description
    }
        for task in tasks]
    return data
