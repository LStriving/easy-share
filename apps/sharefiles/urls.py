from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path(r"folder/user",views.FolderList.as_view()),
    path(r"folder_detail/<int:folder_id>/",views.FolderFiles.as_view(),name='folder_detail'),
    path(r"folder_remove/<int:id>/",views.FolderDelete.as_view(),name='folder_remove'),
    path(r"file/folder/<int:folder_id>",views.SharedFolderDetail.as_view()),
    path(r"file_upload/folder/<int:folder_id>",views.FileCreate.as_view()),
    path(r"file_detail/<int:id>",views.FileDetail.as_view(),name='file_detail'),
]