from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path(r"folder/user",views.FolderList.as_view()),
    path(r"folder/<int:id>",views.FolderInfo.as_view()),
    path(r"folder_detail/<int:folder_id>",views.FolderFiles.as_view(),name='folder_detail'),
    path(r"folder_update/<int:pk>",views.FolderUpdate.as_view(),name='folder_update'),
    path(r"folder_remove/<int:id>",views.FolderDelete.as_view(),name='folder_remove'),
    path(r"file/folder/<int:folder_id>",views.SharedFolderDetail.as_view()),
    path(r"file_upload/folder/<int:folder_id>",views.FileCreate.as_view()),
    path(r"file_detail/<int:id>",views.FileDetail.as_view(),name='file_detail'),
    path(r'file/copy_to_folder/<int:folder_id>',views.copy_files_to_folder,name='copy_local_file'),
    path(r'chunk/folder/<int:folder_id>',views.chunk_file_upload,name='upload_chunk'),
    path(r'large_file_upload_status',views.large_file_upload_status,name='check_upload_status'),
    path(r'large_file_create/folder_id/<int:folder_id>',views.large_file_instance_create,name='create_large_file_instance'),
    path(r'upload',views.FileUploadView.as_view()),
    path(r'folder_list',login_required(views.FolderListWebView.as_view(),login_url='/user/login/')),
    path(r'file_list/<int:folder_id>',login_required(views.FolderDetailView.as_view(),login_url='/')),
    path(r'merge_chunks',views.merge_upload_chunks,name='merge_chunks'),
    path(r'large_file_remove',views.remove_large_file,name='remove_large_file'),
    path(r'check_filename',views.check_filename,name='check_filename'),
    path(r'folder_rename/<int:folder_id>',views.rename_folder,name='folder_rename'),
]