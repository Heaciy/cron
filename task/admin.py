from django.contrib import admin
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask
from django_celery_beat.admin import PeriodicTaskAdmin
from django_celery_results.models import TaskResult
from django_celery_results.admin import TaskResultAdmin


class ExtraTaskResultAdmin(TaskResultAdmin):
    list_display = ('task_id', 'task_name', 'task_obj', 'owner', 'date_done', 'status', 'worker')


class ExtraPeriodicTaskAdmin(PeriodicTaskAdmin):
    list_display = ('__str__', 'owner', 'enabled', 'interval', 'start_time',
                    'last_run_at', 'one_off')


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, ExtraTaskResultAdmin)
admin.site.unregister(PeriodicTask)
admin.site.register(PeriodicTask, ExtraPeriodicTaskAdmin)
