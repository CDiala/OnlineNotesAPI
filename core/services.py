import dataclasses
import datetime
import jwt
from typing import TYPE_CHECKING
from . import models
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import IntegrityError
from rest_framework import response, status

if TYPE_CHECKING:
    from .models import User


"""
A class that represents a user's session, which is used to authenticate the user 
and keep track of their login status in the application.
"""


@dataclasses.dataclass
class UserDataClass:
    '''
    A simple dataclass representing a user object with all its attributes.
    '''
    first_name: str
    last_name: str
    email: str
    password: str = None
    id: int = None

    @classmethod
    def from_instance(cls, user: 'User') -> "UserDataClass":
        '''
        Converts an instance of the User model into this dataclass for easier manipulation and use.
        '''
        return cls(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            id=user.id,
        )


@dataclasses.dataclass
class UserLoginDataClass:
    '''
    A dataclass representing all necessary information about the user who wants to log in.
    '''
    email: str
    password: str = None
    id: int = None

    @classmethod
    def from_instance(cls, user: 'User') -> "UserLoginDataClass":
        '''
        Converts an instance of the User model into this class for use with JWT authentication
        :param user: The user object to convert
        :return: An instance of this class containing data from the given user object
        '''
        return cls(
            email=user.email,
            password=user.password,
            id=user.id,
        )


def create_user(user: "UserDataClass") -> "UserDataClass":
    '''
    Creates and returns an instance of `User` with given data.
    '''
    user_instance = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email
    )

    if user.password is not None:
        user_instance.set_password(user.password)

    user_instance.save()

    return UserDataClass.from_instance(user_instance)


def user_selector(email: str) -> "User":
    '''
    Retrieve a user from database by their email address
    '''
    user = models.User.objects.filter(email=email).first()

    return user


def generate_token(user_id: int) -> str:
    '''
    Generate a JWT token for the given user ID
    '''
    payload = {
        "id": user_id,
        "exp": datetime.datetime.utcnow() +
        datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.JWT_SECRET,
                       algorithm="HS256")

    return token


class Util:
    @staticmethod
    def send_verifyEmail(data):
        '''
        Utility function for sending emails to users
        '''
        try:
            email = EmailMessage(
                subject=data['email_subject'],
                body=data['email_body'],
                to=[data['email_address']]
            )

            if 'file' in data:
                email.attach(
                    data['file'].name,
                    data['file'].read(),
                    data['file'].content_type
                )

            delivery_response = email.send()

            return delivery_response

        except IntegrityError as e:
            return response.Response(
                {"detail": "This account already exists.", "info": e.args[0:]}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return response.Response({'detail': e.args[0:]})
