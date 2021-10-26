from django.urls import path
from . import views

urlpatterns = [
    # FIXME：使用统一的restful不要用复数？
    path('', views.index, name='task'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.get_tasks, name='get_tasks'),
    path('add/', views.add_task, name='add_task'),
    path('results/', views.get_results, name='get_results'),
    path('results_/', views.get_results_by_task, name='get_results_by_task'), # results/1 or results?tid=1
    path('enable/', views.enable_task, name='enable_task'),
    path('run/', views.run_task, name='run_task'),
    path('delete/',views.delete_task,name='delete_task'),
    path('avaible/', views.avaible_tasks, name='avaible_tasks'),
]
