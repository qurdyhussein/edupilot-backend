from django.urls import path
from .views import (
    AdminSignupView,
    admin_login,
    RequestPasswordResetView,
    ConfirmPasswordResetView,
    InstitutionCreateView,
    InstitutionNameCheckView,  # ✅ Import ya view mpya
)

urlpatterns = [
    path('admin/signup/', AdminSignupView.as_view(), name='admin-signup'),
    path('admin/login/', admin_login, name='admin-login'),
    path('password/request-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('password/confirm-reset/', ConfirmPasswordResetView.as_view(), name='confirm-password-reset'),
    path('institutions/', InstitutionCreateView.as_view(), name='institution-create'),
    path('institutions/check-name/', InstitutionNameCheckView.as_view(), name='institution-name-check'),  # ✅ Endpoint mpya
]