import requests
from geopy.geocoders import Nominatim
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from .models import VerificationCode, Profile
from .tokens import account_activation_token


geolocator = Nominatim(user_agent="alg")

def send_confirmation_email(user, request):
    verification_code, created = VerificationCode.objects.get_or_create(user=user)
    verification_code = verification_code.code
    current_site = get_current_site(request)
    email_subject = f"{verification_code} is your Activation Code"
    message = render_to_string('activate_account.html', {
        'user': user,
        'domain': current_site.domain,
        'verification_code': verification_code,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    confirmation_email = EmailMessage(email_subject, message, to=[user.email])
    confirmation_email.send()


def get_user_fb_google(email, facebook_id=None, google_id=None):
    try:
        user = User.objects.get(email=email)
        if user:
            return user
    except ObjectDoesNotExist:
        if facebook_id:
            try:
                user = Profile.objects.get(facebook_id=facebook_id)
                if user:
                    return user.user
            finally:
                pass
        elif google_id:
            try:
                user = Profile.objects.get(google_id=google_id)
                if user:
                    return user.user
            except ObjectDoesNotExist:
                pass
    return None



def get_ip_address(request):
    ip = str()
    try:
        x_forward = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forward:
            ip = x_forward.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
    except:
        pass
    return ip


class GeoApi:
    @staticmethod
    def ip_address(request):
        ip = get_ip_address(request)
        url = f"http://ipinfo.io/{ip}/json"
        data = requests.get(url)
        return data.json()

    @staticmethod
    def geocode(address, exactly_one=True, language="en"):
        locations = geolocator.geocode(address, language="en")
        
        if exactly_one == True:
            return {
                "lat": locations.latitude,
                "lng": locations.longitude,
                "raw": locations.raw,
                "formatted": locations.address,
            }
        else:
            return locations

    @staticmethod
    def reverse(lat="", lng="", language="en"):
        location = f"{lat}, {lng}"
        reversed_location = geolocator.reverse(location, language=language)
        # return reversed_location.address
        return {
            "address": reversed_location.address,
            "raw": reversed_location.raw
        }
