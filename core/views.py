from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
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
        '''
        Method that handles registration of users into the system.
        '''
        try:
            serializer = user_serializer.UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data

            serializer.instance = service.create_user(user=data)

            user_info = serializer.data
            user = User.objects.get(email=user_info['email'])

            SendVerificationEmail.post(self, request)

            return response.Response(data=serializer.data, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return response.Response({'detail': 'Unable to process request.', 'message': e.args[0:]}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return response.Response({'detail': e.args[0:]})


class SendVerificationEmail(views.APIView):
    '''
    View for sending verification emails to registered users.
    '''

    def post(self, request):
        try:
            if not request.data:
                return response.Response({'detail': "No data provided"}, status=status.HTTP_401_UNAUTHORIZED)

            # Get user
            user_email = request.data['email']
            user = User.objects.filter(email=user_email).first()

            if user is not None:
                # Build verification email
                token = RefreshToken.for_user(user).access_token
                current_site = get_current_site(request).domain
                relative_link = reverse('verify-email')
                absolute_url = f'http://{current_site}{relative_link}?token={token}'
                email_body = f'''Hi {user.first_name.title()} {user.last_name.title()},

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

                delivery_response = service.Util.send_verifyEmail(data)

                if delivery_response == 0:
                    return response.Response({'detail': '0 email sent'}, status=status.HTTP_204_NO_CONTENT)
                return response.Response({'detail': '1 email sent sucessfully'}, status=status.HTTP_200_OK)

            return response.Response({'response': "No user found"}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return response.Response({'detail': e.args[0:]}, status=status.HTTP_401_UNAUTHORIZED)


class VerifyEmail(generics.GenericAPIView):
    def get(self, request):
        '''
        This view validates an email after a successful registration and the email verification link is clicked.
        '''
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
        '''
        Log in a user with email/password credentials
        '''
        try:
            request_data = request.data

            serializer = user_serializer.UserLoginSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)

            email = request.data.get("email")
            password = request.data.get("password")

            user = service.user_selector(email)

            if user is None:
                raise exceptions.AuthenticationFailed(
                    "Invalid credentials provided")

            if not user.check_password(raw_password=password):
                raise exceptions.AuthenticationFailed(
                    {"message": "Invalid credentials provided", "code": status.HTTP_401_UNAUTHORIZED})

            token = service.generate_token(user_id=user.id)

            resp = response.Response()

            resp.set_cookie(key="jwt", value=token, httponly=True)
            resp.status_code = 200
            resp.data = {
                "token": token,
                "user": f"{user.first_name.title()} {user.last_name.title()}",
                "id": user.id
            }

            return resp
        except Exception as e:
            return response.Response({'detail': e.args}, status=status.HTTP_400_BAD_REQUEST)


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
    logged in user.
    """
    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        '''
        Erase user session upon logout
        '''
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
        '''
        Updates users password if validations pass
        '''

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
        '''
        Sends reset password link to user via mail
        '''
        try:

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

            email_subject = 'Online NoteTaker - Password Reset'

            email_body = f'''
    Hi {user.first_name} {user.last_name},

    We believe you have requested to reset your password.

    Follow the link below to complete the password reset process.

    {absolute_url}

    Otherwise, disregard the email.

    Stay safe!
    '''

            data = {
                "email_body": email_body,
                "email_subject": email_subject,
                "email_address": user.email
            }

            message_response = service.Util.send_verifyEmail(data)

            if message_response == 1:
                return response.Response({'detail': 'A link has been sent to your email to reset your password.'}, status=status.HTTP_200_OK)
            return response.Response({'detail': 'Failed to deliver email to recipients.'})
        except Exception as e:
            return response.Response({'detail': 'Unable to complete request.', 'message': e.args[0:]}, status=status.HTTP_403_FORBIDDEN)
