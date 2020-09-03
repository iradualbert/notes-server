from rest_framework.serializers import ModelSerializer
from .models import (
    Channel, 
    Product, 
    Listing, 
    Branch, 
    ChannelAdmin, 
    Question, 
    Answer, 
    Review, 
    Subscription
)

class ChannelSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Channel

class SubscriptionSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Subscription
        exclude = ['channel', 'user']

class BranchSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Branch
        read_only_fields = []
class ChannelAdminSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ChannelAdmin
        read_only_fiels = ['user', 'channel']

class ProductSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Product

class ListingSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Listing

class ReviewSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Review

class QuestionSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Question

class AnswerSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Answer
