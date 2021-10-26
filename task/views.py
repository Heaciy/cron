import datetime
import json
from .models import AvlTask
from celery import current_app
from ratelimit.decorators import ratelimit
from task.utils import dumps_kwargs_safe, generate_schedule, serialize_avl_task, serialize_result, serialize_task, parse_task
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_celery_beat.models import PeriodicTask
from django_celery_results.models import TaskResult


def index(request):
    return redirect('dashboard')


def dashboard(request):
    return render(request, 'task/dashboard.html')


@csrf_exempt
@ratelimit(key='ip', rate='10/m')
def add_task(request):
    """添加Task"""
    if request.method == 'POST':
        valid_data = parse_task(request.POST)
        if valid_data.get('valid'):
            data = valid_data.get('data')
            schedule = generate_schedule(data['schedule'], data['sche_str'])
            kwargs = data['kwargs']
            kwargs.update({'uid': request.user.id})
            schedule_kwargs = {'interval': schedule} if data['schedule'] == 'interval' else {
                'crontab': schedule}
            if not PeriodicTask.objects.filter(task=data['task'], **schedule_kwargs).exists():
                PeriodicTask.objects.create(
                    **schedule_kwargs,
                    name=data['name'],
                    task=data['task'],
                    args=json.dumps(data['args']),
                    kwargs=dumps_kwargs_safe(kwargs),
                    expires=datetime.datetime.now() + datetime.timedelta(seconds=30)
                )
            return JsonResponse({'state': 'success'})
        print(valid_data)
        return JsonResponse({'state': 'failed', 'err': valid_data.get('err')})


def get_tasks(request):
    """获取当前用户的所有Task"""
    if request.method == 'GET':
        tasks = PeriodicTask.objects.filter(
            kwargs__icontains=f"\"uid\":{request.user.id}")
        print(tasks)
        data = serialize_task(tasks)
    return JsonResponse({"state": "success", "data": data})


def get_results(request):
    """获取当前用户的所有Result"""
    if request.method == 'GET':
        results = TaskResult.objects.filter(
            task_kwargs__icontains=f"'uid': {request.user.id}")
        data = serialize_result(results)
    return JsonResponse({"state": "success", "data": data})


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


@ratelimit(key='ip', rate='20/m')
def enable_task(request):
    """激活/关闭用户所有的某个task"""
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


@ratelimit(key='ip', rate='20/m')
def run_task(request):  # FIXME: 改为task/run/1,或者post: task/run {tid=1}
    """测试运行用户所属的某个task"""
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


@ratelimit(key='ip', rate='10/m')
def delete_task(request):  # FIXME: 改为task/delete/1, 或者post：task/delete {tid=1}
    """删除当前用户所有的某个task"""
    if request.method == 'GET':
        tid = request.GET.get('tid', None)
        if tid:
            task = PeriodicTask.objects.filter(id=tid).first()
            if task and task.owner == request.user:
                task.delete()
                return JsonResponse({'state': 'success'})
        return JsonResponse({'state': 'failed'})  # TODO: 分类返回err:错误原因


@ratelimit(key='ip', rate='10/m')
def avaible_tasks(request):
    """获取当前用户所有可用tasks"""
    if request.method == 'GET':
        all_tasks = AvlTask.objects.all()
        avl_tasks = [task for task in all_tasks if not task.groups.all(
        ) or request.user.groups.all() & task.groups.all()]
        tasks = serialize_avl_task(avl_tasks)
        # FIXME: 设置过滤列表/添加limit表 task-参数要求-权限(group/superuser/all)
        return JsonResponse({'state': 'success', 'data': tasks})
