import datetime
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, resolve_url
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_celery_results.models import TaskResult


@login_required
def dashboard(request):
    return render(request, 'task/dashboard.html')


@login_required
@csrf_exempt
def add_task(request):
    if request.method == 'POST':
        args = request.POST.get('args')
        task = request.POST.get('task')
        every = request.POST.get('every')
        period = request.POST.get('period')
        task_name = '@'.join([
            # request.user.username,
            task,
            f"{every}-{period}"
        ])
        print(locals())
        print(getattr(IntervalSchedule, period))
        print(request.user.username)
        # print(task_name)
        # now = datetime.datetime.now().strftime("%Y-%M-%d/%H:%M:%S ")
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=int(every), period=getattr(IntervalSchedule, period))
        print(schedule.id)
        if not PeriodicTask.objects.filter(interval=schedule,task=task).exists():
            PeriodicTask.objects.create(
                interval=schedule,
                name=task_name,
                task=task,
                args=json.dumps(json.loads(args)),
                expires=datetime.datetime.now() + datetime.timedelta(seconds=30)
            )
        print(json.dumps(json.loads(args)))
        print("PeriodicTask Already Exists")
        return JsonResponse({"state": "success"})

@login_required
def get_tasks(request):
    if request.method == 'GET':
        username = request.user.username
        tasks = PeriodicTask.objects.filter(name__startswith=username)
        print(tasks)
    return JsonResponse({"state": "success"})

# @login_required
# def get_result(request):
#     if request.method == 'GET':
        
