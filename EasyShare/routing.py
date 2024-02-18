# routing.py
from django.urls import path
from .consumers import SegmentationConsumer

websocket_urlpatterns = [
    path('ws/segmentation/', SegmentationConsumer.as_asgi()),
]
