import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

from questions.routing import websocket_urlpatterns as questions_websocket_urlpatterns
from private_messages.routing import websocket_urlpatterns as messages_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'The_Final_Build.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            questions_websocket_urlpatterns + messages_websocket_urlpatterns
        )
    ),
})