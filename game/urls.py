from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('toss/', views.toss, name='toss'),
    path('choose/', views.choose, name='choose'),
    path('play/', views.play, name='play'),
    path('result/', views.result, name='result'),
]
