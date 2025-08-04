from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import jwt
import datetime
from django.conf import settings
from accounts.models import Profile

RESET_CODE_EXPIRY_MINUTES = getattr(settings, 'RESET_CODE_EXPIRY_MINUTES', 15)

def send_branded_email(subject, to_email, template_name, context):
    html_content = render_to_string(template_name, context)
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email]
    )
    email.content_subtype = 'html'
    email.send()

class AdminSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'message': 'Tafadhali jaza username, email na password.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'message': 'Email tayari imesajiliwa.'},
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

@api_view(["POST", "OPTIONS"])
@permission_classes([AllowAny])
def admin_login(request):
    if request.method == "OPTIONS":
        return Response(status=200)

    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email na password vinahitajika."},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Email au password si sahihi."},
                        status=status.HTTP_401_UNAUTHORIZED)

    authenticated_user = authenticate(username=user.username, password=password)

    if authenticated_user is not None and authenticated_user.is_staff:
        payload = {
            "id": authenticated_user.id,
            "email": authenticated_user.email
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return Response({"token": token}, status=status.HTTP_200_OK)

    return Response({"error": "Email au password si sahihi."},
                    status=status.HTTP_401_UNAUTHORIZED)

class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
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

            return Response({'message': 'Reset code imetumwa kwa email.'}, status=200)

        except User.DoesNotExist:
            return Response({'error': 'Hakuna akaunti yenye email hiyo.'}, status=404)

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