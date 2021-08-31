import datetime
import json
from task.utils import serialize_result, serialize_task

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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
        if not PeriodicTask.objects.filter(interval=schedule, task=task).exists():
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
    """获取当前用户的所有Task"""
    if request.method == 'GET':
        tasks = PeriodicTask.objects.filter(
            kwargs__icontains=f"\"uid\":{request.user.id}")
        print(tasks)
        data = serialize_task(tasks)
    return JsonResponse({"state": "success", "data": data})


@login_required
def get_results(request):
    """获取当前用户的所有Result"""
    if request.method == 'GET':
        results = TaskResult.objects.filter(
            task_kwargs__icontains=f"'uid': {request.user.id}")
        data = serialize_result(results)
    return JsonResponse({"state": "success", "data": data})


# TODO: 直接使用中间件拦截
@login_required
def get_results_by_task(request):
    """通过tid获取本用户所属的result"""
    if request.method == 'GET':
        results = TaskResult.objects.filter(
            task_kwargs__icontains=f"'uid': {request.user.id}")\
            .filter(
            task_kwargs__icontains=f"'tid': {request.GET.get('tid')}")
        print(results)
        data = serialize_result(results)
    return JsonResponse({"state": "success", "data": data})
