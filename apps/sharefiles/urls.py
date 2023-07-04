from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path("folder/<int:id>",views.FolderList.as_view()),
    path("folder_detail/<int:id>",views.FolderDetail.as_view(),name='folder_detail'),
    path("file/<int:id>",views.FileList.as_view()),
    path("file_detail/<int:id>",views.FileDetail.as_view(),name='file_detail'),
]