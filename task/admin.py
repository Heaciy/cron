import json
from django.contrib import admin
from django.contrib.auth.models import User
from django_celery_beat.models import PeriodicTask
from django_celery_beat.admin import PeriodicTaskAdmin
from django_celery_results.models import TaskResult
from django_celery_results.admin import TaskResultAdmin


class ExtraAdmin(admin.ModelAdmin):
    @staticmethod
    def load_from_kwargs(obj, key):
        # 使用getattr同时适配TaskResult和PeriodicTask
        kwargs_str = getattr(obj, "task_kwargs") if hasattr(obj, "task_kwargs")\
            else getattr(obj, "kwargs")
        kwargs = json.loads(kwargs_str.strip("\"").replace('\'', '\"'))
        return kwargs.get(key, None)

    def get_owner(self, obj):
        uid = self.load_from_kwargs(obj, 'uid')
        if uid:
            return User.objects.filter(id=int(uid)).first().username
        return "None"
    get_owner.short_description = 'Owner'


class ExtraTaskResultAdmin(ExtraAdmin, TaskResultAdmin):
    list_display = ('task_id', 'task_name', 'get_owner',
                    'get_task', 'date_done', 'status', 'worker')

    def get_task(self, obj):
        tid = self.load_from_kwargs(obj, 'tid')
        if tid:
            return PeriodicTask.objects.filter(id=int(tid)).first().name
        return ""
    get_task.short_description = 'TaskBeat'


class ExtraPeriodicTaskAdmin(ExtraAdmin, PeriodicTaskAdmin):
    list_display = ('__str__', 'get_owner', 'enabled', 'interval', 'start_time',
                    'last_run_at', 'one_off')


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, ExtraTaskResultAdmin)
admin.site.unregister(PeriodicTask)
admin.site.register(PeriodicTask, ExtraPeriodicTaskAdmin)
