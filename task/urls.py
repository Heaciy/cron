from os import name
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.dashboard,name='dashboard'),
    path('add/', views.add_task, name='add_task'),
    path('tasks/',views.get_tasks,name='get_task'),
    # path('results/',)
]
