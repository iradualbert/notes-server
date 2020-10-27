from .views import (
    ChannelView,
    SubscriptionView,
    ChannelAdminView,
    ProductView, 
    ListingView,
    BranchView,
    ReviewView,
    QuestionView,
    AnswerView
    )
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('api/channels', ChannelView) 
router.register('api/branches', BranchView)
router.register('api/subscriptions', SubscriptionView)
router.register('api/admins', ChannelAdminView)
router.register('api/products', ProductView)
router.register('api/listings', ListingView)
router.register('api/reviews', ReviewView)
router.register('api/questions', QuestionView)
router.register('api/answers', AnswerView)

urlpatterns = [
    path('', include(router.urls)),
    path('api/links/<channel_id>/', ChannelView.add_link),
    path('api/links/<link_id>/delete', ChannelView.destroy_link),
    path('api/channels/<channel_id>/about', ChannelView.about),
]