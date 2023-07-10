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
    return Response(status=status.HTTP_200_OK)


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
    
