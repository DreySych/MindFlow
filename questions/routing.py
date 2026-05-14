from django.urls import path
from .consumers import SimpleDataConsumer

websocket_urlpatterns = [
    path('ws/data/', SimpleDataConsumer.as_asgi()),
]
