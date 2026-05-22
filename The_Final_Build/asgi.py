import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'The_Final_Build.settings')

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from questions.routing import websocket_urlpatterns as questions_websocket_urlpatterns
from private_messages.routing import websocket_urlpatterns as messages_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            questions_websocket_urlpatterns + messages_websocket_urlpatterns
        )
    ),
})