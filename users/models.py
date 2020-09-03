from django.db import models
from django.contrib.auth.models import User
import secrets
import json
import random
from datetime import datetime, timedelta


def generate_integers():
    n = "".join([str(random.randint(0, 9)) for p in range(0, 6)])
    return n

def generate_expire_date():
    expire_date = datetime.now() + timedelta(days=1)
    return expire_date

class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    confirmed = models.BooleanField(default=False)
    is_private = models.BooleanField(default=True)
    gender = models.CharField(max_length=15, blank=True, null=True)
    language = models.CharField(max_length=20, default='en')
    phone_number = models.TextField(null=True, unique=True)
    birthday = models.DateField(null=True)
    facebook_id = models.CharField(max_length=40, null=True, blank=True)
    google_id = models.CharField(max_length=40, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    has_channel = models.BooleanField(default=False)
    use_channel = models.BooleanField(default=False)
    address = models.TextField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    createda_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class VerificationCode(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(default=generate_integers, max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(default=generate_expire_date)

    @staticmethod
    def check_code(user, code):
        try:
            verification_code = VerificationCode.objects.get(
                user=user, code=code)
            if verification_code and verification_code.expire_at > datetime.now():
                return True
            else:
                verification_code.delete() # the code has expired
        except Exception as e:
            pass
        return False

    def __str__(self):
        return f"{self.id}-{self.code}"

class Notification(models.Model):
    to = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='notifications')
    notification_type = models.CharField(null=False, max_length=20)
    body = models.TextField()
    url = models.URLField(null=False)
    seen = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    to_channel = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_json(self):
        return {
            "notification_type": self.notification_type,
            "body": self.body,
            "url": self.url,
            "delivered": self.delivered,
            "seen": self.seen,
            "to_channel": self.to_channel,
            "created_at": self.created_at
        }

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.body} to {self.to.username}"