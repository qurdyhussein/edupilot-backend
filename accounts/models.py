from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    reset_code = models.CharField(max_length=10, blank=True, null=True)
    reset_code_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def is_reset_code_expired(self):
        if not self.reset_code_created_at:
            return True
        expiry_duration = datetime.timedelta(minutes=15)
        return timezone.now() - self.reset_code_created_at > expiry_duration

    def clear_reset_code(self):
        self.reset_code = None
        self.reset_code_created_at = None
        self.save()

class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=255, blank=True)
    contact_1 = models.CharField(max_length=50, blank=True)
    contact_2 = models.CharField(max_length=50, blank=True)
    logo = models.ImageField(upload_to='institutions/logos/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"