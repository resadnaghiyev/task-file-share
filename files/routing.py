from django.urls import re_path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/api/file/(?P<file_id>\w+)/comments/$', ChatConsumer.as_asgi()),
]
