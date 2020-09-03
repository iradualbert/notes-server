from .views import (
     register, 
     activate_account, 
     LoginAPI, 
     update_photo, 
     UserAPI, 
     activate_account_code, 
     degenerate_code, 
     social_authentication,
     ip_address
)
from knox import views as knox_views
from django.urls import path, include


urlpatterns = [
     path('api/auth/ip_address', ip_address),
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
