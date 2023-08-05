from django.shortcuts import render

# Create your views here.


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django.core.mail import send_mail

from .serializers import UserSerializer
from django.contrib.auth.models import User
import jwt
from rest_framework.exceptions import AuthenticationFailed
from jwt.exceptions import ExpiredSignatureError, DecodeError
import datetime

from .serializers import PasswordResetSerializer


@csrf_exempt
@api_view(['POST'])
def create_account(request):
    request.data['username']=request.data['email']
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user=serializer.save()
        user.is_active=False
        user.save()

        # ----------JSON Web Token--------------
        payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'iat': datetime.datetime.utcnow()
    }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response() 
        response.set_cookie(key='activation', value=token, httponly=True) # Set cookie
        
        # ----------Email Send------------
        """
        email=request.data['email']
        email_subject="Activate your account"
        message=f"http://127.0.0.1:8090/auth/verify-account/{token}/"
        send_mail(email_subject,message,settings.EMAIL_HOST_USER,[email])
        response.data="Activation token has been sent in your gmail"
        """
        response.data=f"Your account activation link: http://127.0.0.1:8090/auth/verify-account/{token}/"
        return response
    return Response(serializer.errors, status=400)


@api_view(['GET'])
def account_verify(request,token):
 
    tkn=request.COOKIES.get('activation')
    if not tkn:
        raise AuthenticationFailed('Failed! Register First...')
    
    if token==tkn:
        try:
            payload = jwt.decode(tkn, 'secret', algorithms=['HS256'])
        except ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except DecodeError:
            raise AuthenticationFailed('Unauthenticated!')
    

        user=User.objects.get(id=payload['id'])
        user.is_active=True
        user.save()
        
        return Response("Your account Activated")
    else:
        raise AuthenticationFailed('Something wrong!')



@csrf_exempt
@api_view(['POST'])
def login_user(request):
    email = request.data['email']
    password = request.data['password']
    user = User.objects.filter(email=email).first()

    if user is None:
        raise AuthenticationFailed('User not found!')
    if user.is_active==False:
        raise AuthenticationFailed('Active your account')

    if not user.check_password(password):
        raise AuthenticationFailed('Incorrect password!')     
    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, 'secret', algorithm='HS256')

    response = Response()
    response.set_cookie(key='logintoken', value=token, httponly=True)
    response.data = {"You are logged in"}
    return response

@api_view(['GET'])
def logout_user(request):
    response = Response()
    response.delete_cookie('logintoken')
    response.data = {"you are logged out"}
    return response



@csrf_exempt
@api_view(['POST'])
def request_password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.get(email=serializer.validated_data['email'])
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Expiration after 1 hour
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        reset_link = f"http://127.0.0.1:8090/reset-password/{token}/"

        # Send the reset link to the user's email
        """
        email_subject = "Password Reset"
        message = f"Click the link below to reset your password:\n{reset_link}"
        send_mail(email_subject, message, settings.EMAIL_HOST_USER, [user.email])
        return Response("Password reset link has been sent to your email.")
        """
        respones=Response()
        respones.data={reset_link}
        return respones
    return Response(serializer.errors)


@csrf_exempt
@api_view(['POST'])
def reset_password(request,token):
    new_password = request.data.get('new_password')
    confirm_new_password = request.data.get('confirm_new_password')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except ExpiredSignatureError:
        return Response("Token has expired.")
    except DecodeError:
        return Response("Invalid token.")

    user = User.objects.get(id=payload['id'])

    if new_password == confirm_new_password:
        user.set_password(new_password)
        user.save()
        return Response("Password has been reset successfully.")
    else:
        return Response("New passwords do not match.")




