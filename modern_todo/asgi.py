import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import tasks.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modern_todo.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            tasks.routing.websocket_urlpatterns
        )
    ),
})