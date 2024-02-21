from django.urls import path

from . import views

urlpatterns = [
    path("", view=views.index, name="index"),
    path("monitor-demo",view=views.monitor, name="monitor"),
    path("add_task",view=views.add_task, name="add_task"),
    path(r"tasks",view=views.task_view, name="task"),
    path(r"task_list",view=views.TaskList.as_view(), name="task_list"),
]