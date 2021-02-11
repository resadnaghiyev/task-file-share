import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from files.middleware import JwtAuthMiddlewareStack
import files.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fileshare.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AllowedHostsOriginValidator(
      JwtAuthMiddlewareStack(
          URLRouter(
              files.routing.websocket_urlpatterns
            )
        ),
    ),
})
