from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterAPI.as_view(), name='register'),
    path("verify-email/", views.VerifyEmail.as_view(), name='verify-email'),
    path("password-update/", views.UpdatePassword.as_view(), name='password-update'),
    path("login/", views.LoginAPI.as_view(), name='login'),
    path("me/", views.UserAPI.as_view(), name='me'),
    path("logout/", views.LogoutAPI.as_view(), name='logout')
]
# add endpoints to
# 1. verify email
# 2. send link for email verification to email
# 3. send password reset link to user
# 4. update password

# URL to be sent to email to verify email:
# https://join.com/auth/candidates/verify-login-link?loginToken=fa7da836985a1ffe03d0b612cfe66508f9c06ff4c327f49ef3d82359eb7ecd06163aa187bb3ccd8e4a23c4ae82cd761a97401059b9e2492a5fca85498d90d0f763f49dde4eafbbf6205fc9fe9840be950d0c0a40f223a722dd911c7e2c2723047f0a268fdf060085bd5e6f6b6be1835e8b5ea25e5ab98eef5ff0c9b864d3a5f2&jobId=8488494&userRef=ZGlhbGFjaGlidXpvQHlhaG9vLmNvbQ%3D%3D&pid=d7cb2e8e859c62cd7f75&locale=en-us
#
# EMAIL_VERIFICATION_URL = 'http://localhost:80000/accounts/verify-email/'
