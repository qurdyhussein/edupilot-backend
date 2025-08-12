import datetime
import logging
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveAPIView  # ✅ Added RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import Profile
from .models import Institution
from .serializers import InstitutionSerializer, CustomEmailTokenObtainPairSerializer

logger = logging.getLogger(__name__)
RESET_CODE_EXPIRY_MINUTES = getattr(settings, 'RESET_CODE_EXPIRY_MINUTES', 15)

def send_branded_email(subject, to_email, template_name, context):
    try:
        html_content = render_to_string(template_name, context)
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        email.content_subtype = 'html'
        email.send()
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        raise

class AdminSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'error': 'Tafadhali jaza username, email na password.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email tayari imesajiliwa.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_staff=True
        )

        Profile.objects.get_or_create(user=user)

        return Response({'message': 'Akaunti ya admin imeundwa kwa mafanikio.'},
                        status=status.HTTP_201_CREATED)

class RequestPasswordResetView(APIView):
    throttle_classes = [AnonRateThrottle]
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Tafadhali weka email.'}, status=400)

        try:
            user = User.objects.get(email=email)
            profile, _ = Profile.objects.get_or_create(user=user)

            reset_code = get_random_string(length=6)
            profile.reset_code = reset_code
            profile.reset_code_created_at = timezone.now()
            profile.save()

            send_branded_email(
                subject='EduPilot Password Reset',
                to_email=email,
                template_name='emails/password_reset.html',
                context={'username': user.username, 'reset_code': reset_code}
            )

            masked_email = email[:2] + "****" + email[-10:]
            return Response({'message': f'Reset code imetumwa kwa {masked_email}.'}, status=200)

        except User.DoesNotExist:
            return Response({'error': 'Hakuna akaunti yenye email hiyo.'}, status=404)

        except Exception as e:
            logger.error(f"Error during password reset request: {e}")
            return Response({'error': 'Tatizo limetokea wakati wa kutuma email.'}, status=500)

class ConfirmPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')

        if not email or not code or not new_password:
            return Response({'error': 'Tafadhali jaza email, code na nenosiri jipya.'}, status=400)

        try:
            user = User.objects.get(email=email)
            profile, _ = Profile.objects.get_or_create(user=user)

            if not profile.reset_code or not profile.reset_code_created_at:
                return Response({'error': 'Hakuna reset code iliyohifadhiwa.'}, status=400)

            expiry_time = datetime.timedelta(minutes=RESET_CODE_EXPIRY_MINUTES)
            if timezone.now() - profile.reset_code_created_at > expiry_time:
                return Response({'error': 'Reset code imekwisha muda wake.'}, status=400)

            if profile.reset_code != code:
                return Response({'error': 'Reset code si sahihi.'}, status=400)

            user.set_password(new_password)
            user.save()

            profile.reset_code = None
            profile.reset_code_created_at = None
            profile.save()

            return Response({'message': 'Password imewekwa upya kwa mafanikio.'}, status=200)

        except User.DoesNotExist:
            return Response({'error': 'Mtumiaji hajapatikana.'}, status=404)

class InstitutionCreateView(CreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

class InstitutionDetailView(RetrieveAPIView):  # ✅ Hii ndiyo mpya
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsAdminUser]

class InstitutionNameCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        name = request.query_params.get("name")
        if not name:
            return Response({"error": "Institution name is required."}, status=400)

        name = name.strip()
        exists = Institution.objects.filter(name__iexact=name).exists()
        return Response({"name": name, "exists": exists}, status=200)

class CustomEmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomEmailTokenObtainPairSerializer