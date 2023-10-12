from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from rest_framework import generics, views, response, exceptions, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User
from . import serializers as user_serializer, services as service, authentication
from notebook.models import Owner
import jwt


# Create your views here.


class RegisterAPI(views.APIView):
    '''
    This API is used to register a new user in the system. It takes first_name, 
    last_name, email and password as parameters. Upon creating a new user, an 
    email is sent to their email address, so they can verify their email address.
    '''

    def post(self, request):
        try:
            serializer = user_serializer.UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data

            serializer.instance = service.create_user(user=data)

            user_info = serializer.data
            user = User.objects.get(email=user_info['email'])

            token = RefreshToken.for_user(user).access_token

            current_site = get_current_site(request).domain
            relative_link = reverse('verify-email')
            absolute_url = f'http://{current_site}{relative_link}?token={token}'
            email_body = f'''Hi {user.first_name} {user.last_name},

Welcome onboard! In order to activate your account, please verify your email by clicking on the link below:

{absolute_url}

Can't wait to see more of you on our platform. Until then, take care and be safe

Best regards!
The Team
    '''
            data = {
                "email_body": email_body,
                "email_subject": 'Online NoteTaker - Email Verification',
                "email_address": user.email
            }

            service.Util.send_verifyEmail(data)

            return response.Response(data=serializer.data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return response.Response({'detail': 'Unable to process request.', 'message': e.args[0:]}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return response.Response({'detail': e.args[0:]})


class VerifyEmail(generics.GenericAPIView):
    def get(self, request):
        try:
            token = request.GET.get('token')
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms='HS256')

            user = User.objects.filter(id=payload['user_id']).first()

            owner = Owner.objects.filter(user_id=user.id).first()

            if owner is None:
                owner = Owner()
                owner.user = user

            owner.is_email_valid = True
            owner.save()

            return response.Response({'message': 'Email activated successfully.'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return response.Response({'message': 'Activation link expired.'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.DecodeError:
            return response.Response({'message': 'Invalid token, request new one.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response.Response({'detail': e.args[0:]})


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
    This endpoint updates a user's password by verifying 
    old passwords first then updating it to new one
    '''

    def patch(self, request):

        serializer = user_serializer.UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = request.data.get('email')

        user = get_object_or_404(User, email=user_email)

        new_password = request.data.get('password')

        if new_password:
            user.set_password(request.data.get('password'))

            user.save()
            return response.Response({'detail': 'Password updated successfully'}, status=status.HTTP_200_OK)

        return response.Response({'detail': 'Password not provided'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(views.APIView):
    def post(self, request):

        if not request.data:
            return response.Response({'detail': 'Email field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user_email = request.data.get('email')

        if not user_email:
            return response.Response({'detail': 'Email field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, email=user_email)

        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relative_link = reverse('password-reset')
        absolute_url = f'http://{current_site}{relative_link}?token={token}'

        email_body = f'''
Hi {user.first_name} {user.last_name},

We believe you have requested to reset your password.

Follow the link below to complete the password reset process.

{absolute_url}

Otherwise, disregard the email.

Stay safe!
'''
        # return response.Response('terminated')

        try:
            email = EmailMessage(
                "Request - Password Reset",
                email_body,
                settings.EMAIL_HOST_USER,
                [user.email],
                reply_to=[settings.EMAIL_HOST_USER],
                headers={"Message-ID": "foo"},
            )
            print('\n\n\n\nemail body:', email_body)

            message_response = email.send()

            if message_response == 1:
                return response.Response('A link has been sent to your email to reset your password.', status=status.HTTP_200_OK)
            else:
                return response.Response(f'Failed to deliver email to recipients.')
        except Exception as e:
            return response.Response({'detail': 'Unable to complete request.', 'message': e.args[0:]}, status=status.HTTP_403_FORBIDDEN)
