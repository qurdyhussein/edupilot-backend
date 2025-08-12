from rest_framework import serializers
from .models import Institution
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()

def generate_code(name=None):
    prefix = "INST"
    if name:
        prefix = name.strip().split()[0].upper()
        prefix = ''.join(filter(str.isalnum, prefix))[:6]  # safisha na kata prefix
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{prefix}-{suffix}"

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            'id',
            'name',
            'location',
            'contact_1',
            'contact_2',
            'logo',
            'created_by',
            'created_at',
            'updated_at',
            'code',  # ← hakikisha model bado ina field ya code
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'code']

    def validate_name(self, value):
        value = value.strip()
        if Institution.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Institution name already exists. Tafadhali chagua jina lingine.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["created_by"] = request.user

        # Generate code using name
        name = validated_data.get("name", None)
        validated_data["code"] = generate_code(name)

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