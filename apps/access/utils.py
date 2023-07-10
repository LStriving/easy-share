import string
import random
import redis
from rest_framework import permissions
from EasyShare.celery import app
from django.core.mail import EmailMultiAlternatives,get_connection
from django.template.loader import render_to_string
from EasyShare.settings.base import EMAIL_BACKEND, EMAIL_CODE_EXPIRED_TIME, EMAIL_HOST_USER

r = redis.Redis()

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
    return ''.join(random.choice(letters) for _ in range(length)).upper()

@app.task
def send_verification_email(user_mail,verify_code):
    connection = get_connection(EMAIL_BACKEND)
    subject = 'Verification Code from EasyShare'
    message = render_to_string('verification_code_email.html', 
                            {'verification_code': verify_code,
                             'expired_time':EMAIL_CODE_EXPIRED_TIME // 60})
    email = EmailMultiAlternatives(subject,body='Verification code',
            from_email=EMAIL_HOST_USER,to=[user_mail],connection=connection)
    email.attach_alternative(message, "text/html")
    email.send()

def set_redis_emailcode(email,code):
    r.setex(email,EMAIL_CODE_EXPIRED_TIME,code) # overide value when key exists

def check_redis_emailcode(email,code):
    res = r.get(email)
    if res is not None:
        return res.decode() == code
    return False