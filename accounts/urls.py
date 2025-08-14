from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomEmailTokenObtainPairView,
    AdminSignupView,
    RequestPasswordResetView,
    ConfirmPasswordResetView,
    InstitutionCreateView,
    InstitutionDetailView,           # ✅ Hii imeongezwa
    InstitutionNameCheckView,
    MyInstitutionView,
)

urlpatterns = [
    path('admin/signup/', AdminSignupView.as_view(), name='admin-signup'),
    path('password/request-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('password/confirm-reset/', ConfirmPasswordResetView.as_view(), name='confirm-password-reset'),
    path('institutions/', InstitutionCreateView.as_view(), name='institution-create'),
    path('institutions/<int:pk>/', InstitutionDetailView.as_view(), name='institution-detail'),  # ✅ Hii hapa
    path('institutions/check-name/', InstitutionNameCheckView.as_view(), name='institution-name-check'),
    path('token/', CustomEmailTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('institutions/my/', MyInstitutionView.as_view(), name='my-institution'),
]