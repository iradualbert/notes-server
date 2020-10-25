from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
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
    # is_subscribed = serializers.SerializerMethodField('get_sub_info')
    class Meta:
        model = Channel
        exclude = ['user', 'lat', 'lng', 'created_at']
    
    # def get_sub_info(self, obj):
    #     user =  dir(serializers.CurrentUserDefault())
    #     print(user)
    #     return f"{user}"

class SubscriptionSerializer(ModelSerializer):
    class Meta:
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
    average_rate = serializers.SerializerMethodField('get_average_rate')
    class Meta:
        exclude = ['channel']
        model = Product

    def get_average_rate(self, obj):
        return round(obj.average_rate, 2)

class ListingSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Listing

class ReviewSerializer(ModelSerializer):
    user = serializers.SerializerMethodField('get_user')
    class Meta:
        exclude= ['product', 'likes']
        model = Review
    
    def get_user(self, obj):
        return obj.user.profile.to_json()


class QuestionSerializer(ModelSerializer):
    asked_by = serializers.SerializerMethodField('get_user')
    answers = serializers.SerializerMethodField('get_answers')
    class Meta:
        exclude = ['product']
        model = Question

    def get_user(self, obj):
        return obj.user.profile.to_json()

    def get_answers(self, obj):
        answers = AnswerSerializer(obj.answers.all(), many=True).data
        return answers

class AnswerSerializer(ModelSerializer):
    answered_by = serializers.SerializerMethodField("get_user")
    class Meta:
        exclude = ['question']
        model = Answer

    def get_user(self, obj):
        return obj.user.profile.to_json()
