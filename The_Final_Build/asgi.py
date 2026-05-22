import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns
from private_messages.routing import websocket_urlpatterns as messages_websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "The_Final_Build.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            messages_websocket_urlpatterns +
            notifications_websocket_urlpatterns
        )
    ),
})