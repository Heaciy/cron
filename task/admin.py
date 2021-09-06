from json import loads
from django import forms
from django.contrib import admin
from django_celery_beat.models import PeriodicTask
from django_celery_beat.admin import PeriodicTaskAdmin, TaskChoiceField
from django_celery_results.models import TaskResult
from django_celery_results.admin import TaskResultAdmin
from django.utils.translation import gettext_lazy as _
from .models import AvlTask


class ExtraTaskResultAdmin(TaskResultAdmin):
    list_display = ('task_id', 'task_name', 'task_obj',
                    'owner', 'date_done', 'status', 'worker')


class ExtraPeriodicTaskAdmin(PeriodicTaskAdmin):
    list_display = ('__str__', 'owner', 'enabled', 'interval', 'start_time',
                    'last_run_at', 'one_off')


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, ExtraTaskResultAdmin)
admin.site.unregister(PeriodicTask)
admin.site.register(PeriodicTask, ExtraPeriodicTaskAdmin)


# def tasks_as_choices(self):
#     _ = self._modules  # noqa
#     tasks = list(sorted(name for name in self.celery_app.tasks
#                         if not name.startswith('celery.') and name not in AvlTask.avl_tasks()))
#     return (('', ''), ) + tuple(zip(tasks, tasks))


# TaskChoiceField.widget.tasks_as_choices = tasks_as_choices


class AvlTaskForm(forms.ModelForm):
    task = TaskChoiceField(  # 进一步限制，从复选框中删除已选的(仅限新增时候)
        label=_('Task (registered)'),
        required=False,
    )
    description = forms.CharField(
        label=_('description'),
        widget=forms.Textarea(
            attrs={'placeholder': 'Enter description here (must be jsonable)'})
    )

    class Meta:
        """Form metadata."""

        model = AvlTask
        exclude = ()

    def clean(self):
        data = super().clean()
        regtask = data.get('task')
        if regtask:
            data['task'] = regtask
        if not data['task']:
            exc = forms.ValidationError(_('Need name of task'))
            self._errors['task'] = self.error_class(exc.messages)
            raise exc
        print(data)
        return data

    def _clean_json(self, field):
        value = self.cleaned_data[field]
        try:
            loads(value)
        except ValueError as exc:
            raise forms.ValidationError(
                _('Unable to parse JSON: %s') % exc,
            )
        return value

    def clean_description(self):
        return self._clean_json('description')


@admin.register(AvlTask)
class AvlTaskAdmin(admin.ModelAdmin):
    form = AvlTaskForm
    model = AvlTask
    list_display = ('id', 'name', 'task')
    list_display_links = list_display
    fields = ('name', 'task', 'groups', 'description')
