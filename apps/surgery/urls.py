from django.urls import path

from . import views

urlpatterns = [
    path("", view=views.index, name="index"),
    path("monitor-demo",view=views.monitor, name="monitor"),
    path("add_task",view=views.add_task, name="add_task"),
    path(r"tasks",view=views.task_view, name="task"),
    path(r"task_list",view=views.TaskList.as_view(), name="task_list"),
    path(r"file_result",view=views.result_view, name="result_view"),
    path(r"remove_task/<int:pk>",view=views.delete_task, name="remove_task"),
    path(r"retry_task/<int:pk>",view=views.retry_error_task, name="retry_task"),
]