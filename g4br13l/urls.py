from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.DeepSeekChatView, name='deepseek-chat'),
]