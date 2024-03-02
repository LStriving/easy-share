"""
ASGI config for EasyShare project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from apps.video_rtc.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasyShare.settings.test')

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
    "http": get_asgi_application(),
})
