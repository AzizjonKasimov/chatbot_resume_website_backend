# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/', views.chat_endpoint, name='chat'),
    path('', views.index, name='index'),
]