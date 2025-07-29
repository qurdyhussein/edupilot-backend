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
            return True  # Kama timestamp haipo, angalia kama expired
        expiry_duration = datetime.timedelta(minutes=15)
        return timezone.now() - self.reset_code_created_at > expiry_duration

    def clear_reset_code(self):
        self.reset_code = None
        self.reset_code_created_at = None
        self.save()