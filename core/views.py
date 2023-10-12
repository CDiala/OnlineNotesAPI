# from django.shortcuts import render
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F
from django.urls import reverse
from django.shortcuts import get_object_or_404

from rest_framework import generics, views, response, exceptions, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User
from . import serializers as user_serializer, services as service, authentication
from notebook.models import Owner
import jwt


# Create your views here.


class RegisterAPI(views.APIView):
    '''
    This class handles the registration of a new User in our system 
    and returns an access token for that user if successful or throws 
    appropriate error messages otherwise
    This API is used to register a new user in the system.
    It takes email and password as parameters and returns JSON web 
    token if successful else it will return error message.
    '''

    def post(self, request):
        serializer = user_serializer.UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        serializer.instance = service.create_user(user=data)

        # send verify email to user
        user_info = serializer.data
        user = User.objects.get(email=user_info['email'])

        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relative_link = reverse('verify-email')
        absolute_url = f'http://{current_site}{relative_link}?token={token}'
        email_body = f'''Hi {user.first_name} {user.last_name},

Welcome onboard! In order to activate your account, please verify your email by clicking on the link below:

{absolute_url}

Thank you!
'''
        data = {
            "email_body": email_body,
            "email_subject": 'Email Verification',
            "email_address": user.email
        }

        service.Util.send_verifyEmail(data)

        return response.Response(data=serializer.data, status=status.HTTP_200_OK)


class VerifyEmail(generics.GenericAPIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = get_object_or_404(User, email=payload['email'])

            # not sure if this'll work
            owner = Owner.objects.filter(user_id=F('user__id')).first()

            if owner is None:
                owner.user = user
                owner.is_email_valid = True

                owner.save()
            return response.Response({'message': 'Email activated successfully.'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return response.Response({'message': 'Activation link expired.'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError:
            return response.Response({'message': 'Invalid token, request new one.'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(views.APIView):
    """
    This class handles the login functionality of a User and returns the 
    user's names, id and an access token if successful or raises 401 
    error otherwise
    """

    def post(self, request):

        request_data = request.data

        if not request_data:
            raise exceptions.PermissionDenied(
                "Provide login credentials.", status.HTTP_403_FORBIDDEN)

        email = request.data.get("email")
        password = request.data.get("password")

        user = service.user_selector(email)

        if user is None:
            raise exceptions.AuthenticationFailed(
                "Invalid credentials provided")

        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed(
                "Invalid credentials provided")

        token = service.generate_token(user_id=user.id)

        resp = response.Response()

        resp.set_cookie(key="jwt", value=token, httponly=True)
        resp.status_code = 200
        resp.data = {
            "token": token,
            "user": f"{user.first_name} {user.last_name}",
            "id": user.id
        }

        return resp


class UserAPI(views.APIView):
    """
    This endpoint returns details of logged in user
    """
    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        user = request.user

        serializer = user_serializer.UserSerializer(user)

        return response.Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPI(views.APIView):
    """
    This endpoint logs out the current
    logged in user and deletes their cookie
    """
    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        resp = response.Response()
        resp.delete_cookie("jwt")
        resp.data = {
            "message": "Logout successful"
        }

        return resp


class UpdatePassword(views.APIView):
    '''
    This view updates a user's password by verifying 
    old passwords first then updating it to new one
    '''

    def patch(self, request):

        user_email = request.data.get('email')

        user = get_object_or_404(User, email=user_email)

        print('\n\n\nold pwd', user.password)

        new_password = request.data.get('password')

        if new_password is not None:
            user.set_password(request.data.get('password'))

        # user.password = request.data.get('password')
        print('\n\n\nnew pwd', user.password)
        user.save()
        pass
