from rest_framework import serializers
from .models import Institution

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
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def validate_name(self, value):
        if Institution.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Institution name already exists.")
        return value

    def validate_code(self, value):
        if Institution.objects.filter(code__iexact=value).exists():
            raise serializers.ValidationError("Institution code already exists.")
        if not value.isalnum():
            raise serializers.ValidationError("Code must be alphanumeric.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)