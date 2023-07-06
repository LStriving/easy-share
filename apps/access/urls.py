from django.urls import path

from . import views

urlpatterns = [
    path(r"",views.UserRegisterAPIView.as_view(),name='register'),
    path(r'<int:pk>',views.UserRetrieveUpdateView.as_view(),name='view&update'),
    path(r'password',views.change_password,name='change_password'),

]
