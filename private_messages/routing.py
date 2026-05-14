from django.urls import path

from .consumers import PersonalMessageConsumer

websocket_urlpatterns = [
    path('ws/chat/<int:user_id>/', PersonalMessageConsumer.as_asgi()),
]
