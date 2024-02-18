
from django.urls import path
from .views import upload_frame,demoWeb,socketWeb

urlpatterns = [
    path('upload_frame/', upload_frame, name='upload_frame'),
    path(r"demo2/",socketWeb.as_view(),name="demo2"),
    path("",demoWeb.as_view(),name='demo')
]
