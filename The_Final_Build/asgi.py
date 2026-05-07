import os
from channels.routing import ProtocolTypeRouter, URLRouter
from questions.routing import websocket_urlpatterns
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'The_Final_Build.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(), # Для обычных страниц
    "websocket": URLRouter(
        websocket_urlpatterns # Для сокетов
    ),
})