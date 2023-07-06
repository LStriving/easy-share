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
        user.set_password
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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    '''
        post:
            user change account password
    '''
    # get the JSON data from the request body
    data = request.data
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
    logout(request)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET','POST'])
@permission_classes([permissions.AllowAny])
def send_email_code(request):
    data = json.loads(request.body)
    code = generate_verification_code()
    email = data['email']
    send_verification_email(email,code)
    EmailCode.objects.create(email=email,code=code)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET','POST'])
@permission_classes([permissions.AllowAny])
def reset_password_with_email(request):
    data = json.loads(request.body)
    email = data['email']
    code = data['code']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try:
        EmailCode.objects.get(email=email,code=code)
        user.set_password(data['password'])
        return Response(status=status.HTTP_200_OK)
    except EmailCode.DoesNotExist:
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)