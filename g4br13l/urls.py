# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.TestView, name='test'),
    path('chat/', views.DeepSeekChatView.as_view(), name='deepseek-chat'),
    path('chat-stream/', views.DeepSeekStreamView.as_view(), name='deepseek-stream'),
]