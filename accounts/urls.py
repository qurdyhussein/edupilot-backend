# accounts/urls.py
from django.urls import path
from .views import AdminSignupView
from .views import AdminLoginView
from .views import RequestPasswordResetView
from .views import ConfirmPasswordResetView

urlpatterns = [
    path('admin/signup/', AdminSignupView.as_view(), name='admin-signup'),
    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),
    path('password/request-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('password/confirm-reset/', ConfirmPasswordResetView.as_view(), name='confirm-password-reset'),
]