import dataclasses
import datetime
import jwt
from typing import TYPE_CHECKING
from . import models
from django.conf import settings

if TYPE_CHECKING:
    from .models import User


"""
A class that represents a user's session, which is used to authenticate the user 
and keep track of their login status in the application.
"""


@dataclasses.dataclass
class UserDataClass:
    first_name: str
    last_name: str
    email: str
    password: str = None
    id: int = None

    @classmethod
    def from_instance(cls, user: 'User') -> "UserDataClass":
        return cls(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            id=user.id,
        )


"""
JWT Token Structure
"""


def create_user(user: "UserDataClass") -> "UserDataClass":
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
    user = models.User.objects.filter(email=email).first()

    return user


def generate_token(user_id: int) -> str:
    payload = {
        "id": user_id,
        "exp": datetime.datetime.utcnow() +
        datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.JWT_SECRET,
                       algorithm="HS256")

    return token
