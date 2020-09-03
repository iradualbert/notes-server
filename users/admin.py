from django.contrib import admin
from .models import Profile, VerificationCode, Notification
# Register your models here.

admin.site.register(Profile)
admin.site.register(VerificationCode)
admin.site.register(Notification)
