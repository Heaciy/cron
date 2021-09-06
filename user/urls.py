from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='user'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('get_captcha', views.send_captcha, name='get_captcha'),
]
