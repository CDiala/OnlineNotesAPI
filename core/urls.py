from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterAPI.as_view(), name='register'),
    path("send-verification-email/", views.SendVerificationEmail.as_view(),
         name='send-verification-email'),
    path("verify-email/", views.VerifyEmail.as_view(), name='verify-email'),
    path("password-reset/", views.ResetPassword.as_view(), name='password-reset'),
    path("password-update/", views.UpdatePassword.as_view(), name='password-update'),
    path("login/", views.LoginAPI.as_view(), name='login'),
    path("me/", views.UserAPI.as_view(), name='me'),
    path("logout/", views.LogoutAPI.as_view(), name='logout')
]
