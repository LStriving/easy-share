import string
import random
from rest_framework import permissions
from django.core.mail import send_mail
from django.template.loader import render_to_string
from EasyShare.settings import EMAIL_HOST_USER

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # check if the user is the owner or an admin
        # print(f"Staff:{request.user.is_staff}")
        return request.user == obj.user or request.user.is_staff
    

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # check if the user is the owner or an admin
        return request.user == obj.user 
    
class IsSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj
    

def generate_verification_code(length=6):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def send_verification_email(user_mail,verify_code):
    subject = 'Verification Code from EasyShare'
    message = render_to_string('verification_code_email.html', {'verification_code': verify_code})
    send_mail(subject,message,from_email=EMAIL_HOST_USER,recipient_list=[user_mail])