from django.db import models
from django.contrib.auth import models as auth_models

# Create your models here.


class UserManager(auth_models.BaseUserManager):

    def create_user(self, first_name: str, last_name: str, email: str, password: str = None, is_staff: bool = False, is_superuser: bool = False) -> "User":
        '''
        Custom user model manager where email is the unique identifier.
        '''

        if not first_name:
            raise ValueError("The 'First Name' field must be set.")
        if not last_name:
            raise ValueError("The 'Last Name' field must be set.")
        if not email:
            raise ValueError("The Email field must be set.")
        if not password:
            raise ValueError("The 'Password' field must be set.")

        email = self.normalize_email(email)
        user = self.model(email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = True
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, first_name: str, last_name: str, email: str, password: str) -> "User":
        '''
        Create and save a new superuser with given details
        '''
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )

        user.save()

        return user


class User(auth_models.AbstractUser):
    '''
    Custom user model that supports using only email for authentication.
    '''
    first_name = models.CharField(verbose_name="First Name", max_length=255)
    last_name = models.CharField(verbose_name="Last Name", max_length=255)
    email = models.EmailField(verbose_name="Email",
                              max_length=255, unique=True)
    password = models.CharField(verbose_name="Password", max_length=255)
    date_joined = models.DateTimeField(
        verbose_name="Date Joined", auto_now_add=True)
    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self) -> str:
        return f"{self.email}"
