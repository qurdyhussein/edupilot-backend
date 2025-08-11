from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    AdminSignupView,
    RequestPasswordResetView,
    ConfirmPasswordResetView,
    InstitutionCreateView,
    InstitutionNameCheckView,
)

urlpatterns = [
    path('admin/signup/', AdminSignupView.as_view(), name='admin-signup'),
    path('password/request-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('password/confirm-reset/', ConfirmPasswordResetView.as_view(), name='confirm-password-reset'),
    path('institutions/', InstitutionCreateView.as_view(), name='institution-create'),
    path('institutions/check-name/', InstitutionNameCheckView.as_view(), name='institution-name-check'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]