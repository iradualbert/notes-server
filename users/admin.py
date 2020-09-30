from django.contrib import admin
from .models import Profile, VerificationCode, Notification, History, Saved
# Register your models here.

admin.site.register(Profile)
admin.site.register(VerificationCode)
admin.site.register(Notification)
admin.site.register(Saved)
admin.site.register(History)