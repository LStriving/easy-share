from django.urls import path

from . import views

urlpatterns = [
    path(r"",views.UserRegisterAPIView.as_view(),name='register'),
    path(r'<int:pk>',views.UserRetrieveUpdateView.as_view(),name='view&update'),
    path(r'password',views.change_password,name='change_password'),
    path(r'logout',views.logout_view,name='logout'),
    path(r'reset_password',views.reset_password_with_email),
    path(r'send_code',views.send_email_code)
]
