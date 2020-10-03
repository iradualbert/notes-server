import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from rest_framework import generics, permissions
from rest_framework import serializers
from rest_framework.decorators import api_view
from knox.models import AuthToken
from .tokens import account_activation_token
from .models import Profile, VerificationCode
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .utils import send_confirmation_email, get_user_fb_google

@api_view(['POST', 'DELETE', 'PUT'])
def update_photo(request):
    user = request.user
    if user.is_authenticated:
        profile = user.profile
        profile.photo.delete()
        if request.method == "POST":
            data = json.loads(request.body)
            profile.photo = data.get('photo')
        elif request.method == "DELETE":
            profile.photo = None
        profile.save()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'error': 'bad request'}, status=401)



@api_view(['POST'])
def register(request):
    data = request.data
    data["first_name"] = data.get('fullname')
    serializer = RegisterSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        Profile.objects.create(user=user)
        send_confirmation_email(user, request)
        _, token = AuthToken.objects.create(user)
        return JsonResponse({
            "user": UserSerializer(user).data,
            "token": token,
            "is_active": user.profile.confirmed
        })
        
   


# activate through email
@api_view(['GET'])
def activate_account(request, uidb64, token):
    uid = force_bytes(urlsafe_base64_decode(uidb64))
    try:
        user = User.objects.get(pk=uid)
        if user is not None and account_activation_token.check_token(user, token):
            profile = user.profile
            profile.confirmed = True
            profile.save()
            return JsonResponse({'status': f"{user}"})
    finally:
        pass
    return JsonResponse({'error': 'invalid activation link'})


# activate through code
@api_view(['POST'])
def activate_account_code(request):
    user = request.user
    data = json.loads(request.body)
    code = data.get('code')
    if not user.is_authenticated:
        return JsonResponse({'detail': 'Authentication issues'}, status=401)
    if not code:
        return JsonResponse({'code': 'Invalid code'}, status=400)
    if VerificationCode.check_code(user, code):
        return JsonResponse({
            "user": UserSerializer(user).data,
            "is_active": True
        })
    else:
        return JsonResponse({'code': 'Invalid code'}, status=400)


@api_view(['POST'])
def degenerate_code(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"detail": "Authentication issues"})
    send_confirmation_email(user, request)
    return JsonResponse({'status': 'ok'})


# Login API
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        _, token = AuthToken.objects.create(user)
        return JsonResponse({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token,
            "is_active": user.profile.confirmed
        })

# social authentication


@api_view(['POST'])
def social_authentication(request):
    account_exist = False
    data = json.loads(request.body)
    email = data.get('email')
    facebook_id = data.get('facebook_id')
    google_id = data.get('google_id')
    fullname = data.get('fullname')
    if not email or not(google_id or facebook_id):
        return JsonResponse({'error': 'missing data'})
    # check if the user exists
    user = get_user_fb_google(
        email, facebook_id=facebook_id, google_id=google_id)
    profile = None
    if user:
        account_exist = True
        profile = user.profile
    # create new account
    else:
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            Profile.objects.create(user=user, fullname=fullname, confirmed=True,
                                   google_id=google_id, facebook_id=facebook_id)
        else:
            return JsonResponse(serializer.errors, status=400)
    if facebook_id and not profile.facebook_id:
        profile.facebook_id = facebook_id
    elif google_id and not profile.google_id:
        profile.google_id = google_id
    profile.save()
    _, token = AuthToken.objects.create(user)
    return JsonResponse({
        'token': token,
        "user": {
            'username': user.username,
            'email': user.email
        },
        "account_found": account_exist
    })

# Get User API
class UserAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

