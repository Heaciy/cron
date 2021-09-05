from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='task'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.get_tasks, name='get_task'),
    # path('add/', views.add_task, name='add_task'),
    path('results/', views.get_results, name='get_results'),
    path('results_/', views.get_results_by_task, name='get_results_by_task'),
    path('enable/', views.enable_task, name='enable_task'),
    path('run/', views.run_task, name='run_task'),
    path('add/', views.add_interval_task, name='add_task'),
]
