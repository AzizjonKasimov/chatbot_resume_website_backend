# resume_website_backend/chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_endpoint, name='chat'),
    path('feedback/', views.feedback_email, name='feedback'),
    path('',          views.index,         name='index'),
]