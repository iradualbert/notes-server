from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Profile

@api_view(['GET'])
def get_user_info(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'detail': 'not authenticated'}, status=401)
    profile = user.profile
    channel = None
    try:
        channel = user.channel
    except Exception as e:
        pass
    reviews = user.reviews.all().count()
    questions = user.asked.all().count()
    profile_data = profile.to_json()
    channel_data = {}
    if channel:
        channel_data = {
            "name": channel.name,
            "subscribers": channel.subscribers.all().count(),
            "id": channel.id,
            "photo": channel.photo,
            "total_posts": channel.products.all().count()
            }
    user_data = {
        "fullname": user.first_name,
        "username": user.username,
        "email": user.email,
        "id": user.id,
        "language": profile.language,
        "address": profile.address,
        "country": profile.country,
        "phone_number": profile.phone_number,
        "birthday": profile.birthday,
        "gender": profile.gender,                
        "photo": profile.photo,
        "reviews": reviews,
        "questions": questions
        }

    return Response({
        "channel": channel_data,
        "user": user_data
        })


@api_view(['GET'])
def get(request, requested=""):
    user = request.user
    if not user.is_authenticated:
        return Response({'detail': 'not authenticated'}, status=401)
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 6))
    to_fetch = limit + 1
    fetched = []
    if requested == "reviews":
        fetched = user.reviews.all()[offset:offset+to_fetch]
    elif requested == "questions":
        fetched = user.asked.all()[offset:offset+to_fetch]
    elif requested == "saved":
        fetched = user.saved.all()[offset:offset+to_fetch]
    elif requested == "subscriptions":
        fetched = user.subscriptions.all()[offset:offset+to_fetch]
    elif requested == "notifications":
        fetched = user.notifications.all()[offset:offset+to_fetch]
    else:
        raise ValueError("you can only request for reviews, questions, saved, subscriptions")
    more_available = len(fetched) == limit
    data = [x.to_json() for x in fetched[0:limit]]
    return Response({
        requested: data,
        "more_available": more_available
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def user_library(request):
    user = request.user
    saved = user.saved.all().count()
    subscriptions = user.subscriptions.all().count()
    reviews = user.reviews.all().count()
    questions = user.asked.all().count()
    
    return Response({
        "saved": saved,
        "subscriptions": subscriptions,
        "reviews": reviews,
        "questions": questions,
    }, status=200)
     

@api_view(['GET'])
def get_saved(request):
    return Response({}, status=200)

class UserInfo:
    @staticmethod
    def info(request):
        return get_user_info(request)
    @staticmethod
    def library(request):
        return user_library(request)
    @staticmethod
    def notifications(request):
        return get(request, requested="notifications")
    @staticmethod
    def reviews(request):
        return get(request,requested="reviews")

    @staticmethod
    def questions(request):
        return get(request, requested="questions")

    @staticmethod
    def saved(request):
        return get(request, requested="saved")
   
    @staticmethod
    def subscriptions(request):
        return get(request, requested="subscriptions")

    