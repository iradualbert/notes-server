from .views import (
     register, 
     activate_account, 
     LoginAPI, 
     update_photo, 
     UserAPI, 
     activate_account_code, 
     degenerate_code, 
     social_authentication,
     get_location
)
from .views_info import (
     get_user_info,
     UserInfo
)
from knox import views as knox_views
from django.urls import path, include


urlpatterns = [
     # views_info
     path('api/user/location', get_location),
     path('api/user/reviews', UserInfo.reviews, name="user_reviews"),
     path('api/user/info', UserInfo.info, name="user_info"),
     path('api/user/notifications', UserInfo.notifications, name="user_notifications"),
     path('api/user/questions', UserInfo.questions, name="user_questions"),
     path('api/user/subscriptions', UserInfo.subscriptions, name="user_subscriptions"),
     path('api/user/saved', UserInfo.saved, name="user_subscriptions"),
     
    # views
    path('api/auth', include('knox.urls')),
    path('api/auth/register', register),
    path('api/auth/user', UserAPI.as_view()),
    path('api/auth/login', LoginAPI.as_view()),
    path('api/auth/logout', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('api/auth/logoutall', knox_views.LogoutAllView.as_view(),
         name='knox_logout_all'),
    path('api/auth/social-auth', social_authentication),
    path('api/accounts/activate/<uidb64>/<token>',
         activate_account, name='activate'),
    path('api/accounts/activate/code',
         activate_account_code, name="activate-code"),
    path('api/accounts/activate/resend', degenerate_code),
    path('api/accounts/update_photo', update_photo),
]
