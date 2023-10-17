from django.conf import settings
import jwt
from rest_framework import authentication, exceptions
from . import models


class CustomUserAuthentication(authentication.BaseAuthentication):
    '''
    This class is responsible for authenticating a user based on their token.
    '''

    def authenticate(self, request):

        # Extract the JWT from the Authorization header
        token = request.COOKIES.get(
            "jwt") or request.META.get('HTTP_AUTHORIZATION')

        if not token:
            return None

        if ('Bearer' in token) or (str(token).startswith('Bearer')):
            token = str(token).replace('Bearer', '').strip()

        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=['HS256'])

        except:
            raise exceptions.AuthenticationFailed("Unauthorized")

        user = models.User.objects.filter(id=payload["id"]).first()

        return (user, None)

        # return super().authenticate(request)
