import datetime
import json
from celery import current_app
from ratelimit.decorators import ratelimit
from task.utils import dumps_kwargs_safe, parse_data_form, serialize_result, serialize_task
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_celery_results.models import TaskResult

@login_required
def index(request):
    return redirect('dashboard')

@login_required
def dashboard(request):
    return render(request, 'task/dashboard.html')

# TODO：设置一个通用的add_task
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


@login_required
@ratelimit(key='ip', rate='20/m')
def enable_task(request):
    if request.method == 'GET':
        tid = request.GET.get('tid', None)
        if tid:
            task = PeriodicTask.objects.get(id=int(tid))
            if task.owner == request.user:
                task.enabled = not task.enabled
                task.save()
                print(task.enabled)
                return JsonResponse({'state': 'success', 'enabled': task.enabled})
        return JsonResponse({'state': 'failed'})


@login_required
@ratelimit(key='ip', rate='20/m')
def run_task(request):
    if request.method == 'GET':
        tid = request.GET.get('tid', None)
        if tid:
            task_obj = PeriodicTask.objects.get(id=int(tid))
            # if task_obj.owner.id == request.user.id and task_obj.enabled == True:
            if task_obj.owner == request.user:
                current_app.loader.import_default_modules()
                task = current_app.tasks.get(task_obj.task)
                if task:
                    args = json.loads(task_obj.args)
                    kwargs = json.loads(task_obj.kwargs)
                    queue = task_obj.queue
                    if queue and len(queue):
                        task.apply_async(args=args, kwargs=kwargs)
                    else:
                        task.apply_async(args=args, kwargs=kwargs, queue=queue)
                    return JsonResponse({'state': 'success'})
        return JsonResponse({'state': 'failed'})


@login_required
@csrf_exempt
@ratelimit(key='ip', rate='10/m')
def add_interval_task(request):
    if request.method == 'POST':
        valid_data = parse_data_form(request.POST)
        if valid_data.get('valid'):
            data = valid_data.get('data')
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=int(data['every']), period=getattr(IntervalSchedule, data['period']))
            kwargs = data['kwargs']
            kwargs.update({'uid': request.user.id})
            if not PeriodicTask.objects.filter(interval=schedule, task=data['task']).exists():
                PeriodicTask.objects.create(
                    interval=schedule,
                    name=data['name'],
                    task=data['task'],
                    args=json.dumps(data['args']),
                    kwargs=dumps_kwargs_safe(kwargs),
                    expires=datetime.datetime.now() + datetime.timedelta(seconds=30)
                )
            return JsonResponse({'state': 'success'})
        print(valid_data)
        return JsonResponse({'state': 'failed', 'err': valid_data.get('err')})
