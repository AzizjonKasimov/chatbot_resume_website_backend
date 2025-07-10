# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_endpoint, name='chat'),
    path('',          views.index,         name='index'),
]