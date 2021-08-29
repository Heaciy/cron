from django_celery_beat.models import IntervalSchedule, PeriodicTask
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
