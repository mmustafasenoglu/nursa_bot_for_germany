from django.urls import path
from .views import ChatAPIView, HealthCheckView, ChatHistoryView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('chat/history/', ChatHistoryView.as_view(), name='chat-history'),
]
