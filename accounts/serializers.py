from rest_framework import serializers
from .models import Institution
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            'id',
            'name',
            'code',
            'location',
            'contact_1',
            'contact_2',
            'logo',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_name(self, value):
        value = value.strip()
        if Institution.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Institution name already exists. Tafadhali chagua jina lingine.")
        return value

    def validate_code(self, value):
        value = value.strip()
        if Institution.objects.filter(code__iexact=value).exists():
            raise serializers.ValidationError("Institution code already exists. Tafadhali tumia code nyingine.")
        if not value.isalnum():
            raise serializers.ValidationError("Code must be alphanumeric (herufi na namba tu).")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)

class CustomEmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email au password si sahihi.")

        if not user.check_password(password):
            raise serializers.ValidationError("Email au password si sahihi.")

        refresh = self.get_token(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }