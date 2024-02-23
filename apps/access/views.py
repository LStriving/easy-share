from rest_framework import permissions,status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView,RetrieveUpdateAPIView
from django.contrib.auth import authenticate,login
from apps.access.utils import *
import json

from .models import User
from .serializers import *
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.core.mail import send_mail
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.views import LoginView

class UserRegisterAPIView(CreateAPIView):
    """
        post:
            user registration
    """
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        # create a user instance using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request,user)
        # return a JSON response with the token and the user data
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    '''
        get:
            get user info
        put:
            update user info
        patch:
            partially update user info
    '''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelf]

# TODO: not working
class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Login successful.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Login failed. Please check your credentials.', extra_tags='login_failed')
        return super().redender_to_response(self.get_context_data(form=form),messages=messages)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    '''
        post:
            user change account password
    '''
    # get the JSON data from the request body
    if request.method == 'GET':
        data = request.GET
    else:
        data = json.loads(request.body)
    # do something with the data
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    user = authenticate(username=request.user.username,password=old_password)
    if user is None:
        return Response(data={'message':'Password error'},status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        user.set_password(new_password)
        return Response(status=status.HTTP_200_OK)


@api_view(['GET','POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    '''
        get:
            logout
        post:
            logout
    '''
    logout(request)
    return redirect('login')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def send_email_code(request):
    if request.method == 'GET':
        data = request.GET
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    code = generate_verification_code()
    try:
        email = data['email']
    except KeyError:
        return Response(data={'message':"'email' field is required"},
                        status=status.HTTP_400_BAD_REQUEST)
    send_verification_email.delay(email,code)
    set_redis_emailcode(email,code)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET','POST'])
@permission_classes([permissions.AllowAny])
def reset_password_with_email(request):
    if request.method == 'GET':
        data = request.GET
    else:
        data = request.POST
    try:
        email = data['email']
        code = data['code']
    except KeyError:
        return Response(data={'message':"'email' and 'code' fields are both required,\
                            \n check request content type (multipart-form data)"},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(data={'message':'Email not registered!'},
                        status=status.HTTP_404_NOT_FOUND)
    if not check_redis_emailcode(email,code):
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        user.set_password(data['password'])
        user.save()
        return Response(status=status.HTTP_200_OK)
    
@permission_classes([permissions.AllowAny])
def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            try:
                User.objects.get(email=email)
                return Response(status=status.HTTP_409_CONFLICT,data={'message':'Email already exists'})
            except User.DoesNotExist:
                pass
            try:
                User.objects.get(username=username)
                return Response(status=status.HTTP_409_CONFLICT,data={'message':'Username already exists'})
            except User.DoesNotExist:
                pass
            try:
                # TODO: set timeout or delay
                send_mail(
                    'Welcome to EasyShare',
                    f'Congratulations, {username}!\n' 
                    'You have successfully registered an account on EasyShare!',
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[email],
                    )
                form.save()
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,data={'message':'Email sending failed'})
            user = User.objects.get(username=username)
            login(request,user)
            return redirect('login')
        else:
            print(form.errors.as_text())
    else:
        form = SignUpForm()
    
    return render(request, 'register.html', {'error': form.errors.as_json()})
