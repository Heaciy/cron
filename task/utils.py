import re
import json
from datetime import datetime
from typing import Dict, List
from django.conf import settings
from django.core.exceptions import ValidationError
from django_celery_beat.models import IntervalSchedule, CrontabSchedule, PeriodicTask
from django_celery_beat.validators import crontab_validator
from django_celery_results.models import TaskResult
from task.models import AvlTask


def load_from_kwargs(obj, key):
    """使用getattr同时适配TaskResult和PeriodicTask"""
    kwargs_str = getattr(obj, "task_kwargs") if hasattr(obj, "task_kwargs") \
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
        'tid': task.id,
        'owner': str(task.owner),
        'interval': str(task.interval),
        'crontab': str(task.crontab),
        'args': load_args_from_str(task.args),
        'kwargs': load_kwargs_from_str_safe(task.kwargs),
        'enabled': str(task.enabled),
        'total_run_count': task.total_run_count,
        'date_changed': load_strftime_from_datetime(task.date_changed),
        # 'description': task.description
        'description': f'{task.interval if task.interval else task.crontab}'
    }
        for task in tasks]
    return data


def load_description_safe(description):
    description = description.replace('\n', '').replace('\r', '')
    description = re.sub(r' +', '', description)
    return description


def serialize_avl_task(tasks) -> List[Dict]:
    data = [{
        'name': task.name,
        'task': task.task,
        'description': load_description_safe(task.description),
    } for task in tasks]
    return data


def dumps_kwargs_safe(kwargs):
    return json.dumps(kwargs).replace(': ', ':').replace(', ', ',')


def valid_interval(sche_str):
    try:
        every, period = sche_str.strip().split('/')
        if int(every) > 0 and period.lower() in settings.AVL_PERIOD:
            return True
        return False
    except Exception as e:
        return False


def valid_crontab(sche_str):
    try:
        print(sche_str)
        tmp = sche_str.strip().split()
        if len(tmp) != 5:
            return False
        tab = ['*'] * 5
        for i, j in enumerate(tmp):
            tab[i] = j
        tab = ' '.join(tab)
        print(tab)
        crontab_validator(tab)
        return True
    except Exception as e:
        print(e)
        return False


def valid_str(sche_str):
    return sche_str.strip().lower()


def valid_schedule(schedule, sche_str):
    if schedule not in settings.AVL_SCHEDULE:
        return False
    try:
        # 动态获取当前作用域下的验证方法
        valid_func = globals()[f'valid_{schedule}']
        if valid_func(sche_str):
            return True
        return False
    except Exception as e:
        return False


def generate_schedule(schedule, sche_str):
    # 根据schedule, sche_str生成schedule对象
    sche_str = valid_str(sche_str)
    if valid_schedule(schedule, sche_str):
        gen_func = globals()[f'get_{schedule}_schedule']
        return gen_func(sche_str)
    raise ValidationError


def get_interval_schedule(valid_str):
    # 单例模式
    every, period = valid_str.strip().split('/')
    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=int(every), period=period)
    return schedule


def get_crontab_schedule(valid_str):
    # 单例模式
    schedule = None
    args = valid_str.strip().split(' ')
    if len(args) == 5:
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=args[0], hour=args[1], day_of_week=args[2], day_of_month=args[3], month_of_year=args[4])
    elif len(args) == 6:
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=args[0], hour=args[1], day_of_week=args[2], day_of_month=args[3], month_of_year=args[4],
            timezone=args[5])
    return schedule


def parse_task(data):
    """从Post的form中解析数据"""
    data = json.loads(data.get('data'))
    data = {
        'name': data.get('name', None),
        'task': data.get('task', None),
        'args': data.get('args', list()),
        'kwargs': data.get('kwargs', dict()),
        'schedule': data.get('schedule', None),
        'sche_str': data.get('schedule_str', None)
    }
    err = []
    if PeriodicTask.objects.filter(name=data['name']).exists():
        err.append(f'Task name {data["name"]} already in use!')
    if not data['task'] in AvlTask.avl_tasks():  # 需要校验用户是否满足
        err.append(f'Task {data["task"]} not exist!')
    if not isinstance(data['args'], list):
        err.append(f'Args must be a list!')
    if not isinstance(data['kwargs'], dict):
        err.append(f'Kwargs must be a dict!')
    if not valid_schedule(data['schedule'], data['sche_str']):
        err.append(f'Schedule str invalid!')
    valid = False if err and len(err) else True
    return {'valid': valid, 'data': data, 'err': err}
