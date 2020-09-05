import json
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import (
    ChannelSerializer, 
    BranchSerializer,
    ChannelAdminSerializer,
    ProductSerializer, 
    ListingSerializer,
    ReviewSerializer,
    QuestionSerializer,
    AnswerSerializer,
    SubscriptionSerializer,
)
from .models import (
    Channel, 
    ChannelAdmin, 
    Branch,
    Subscription,
    Product, 
    Listing, 
    Review,
    Question,
    Answer
)


class ChannelView(ModelViewSet):
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()

class SubscriptionView(ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    permission_classes = (permissions.IsAuthenticated, )


    def get_queryset(self):
        request = self.request
        user = request.user
        return user.subscriptions.all()
    
    def perform_create(self, serializer):
        user = self.request.user
        channel_id = self.request.GET.get('channel_id')
        channel = Channel.objects.get(id=channel_id)
        serializer.save(user=user, channel=channel)


class ChannelAdminView(ModelViewSet):
    serializer_class = ChannelAdminSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ChannelAdmin.objects.all()


    def create(self, request, *args, **kwargs):
        user = request.user
        channel_id = request.GET.get("channel_id")
        try:
            channel = Channel.objects.get(user=user, id=channel_id)
        except ObjectDoesNotExist:
            return Response({'detail': 'channel not found'}, status=404)
        data = json.loads(request.body)
        serializer = ChannelAdminSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user, channel=channel)
        else:
            return Response(serializer.errors, status=400)
        return Response(serializer.data, status=201)


class BranchView(ModelViewSet):
    serializer_class = BranchSerializer
    queryset = Branch.objects.all()


class ListingView(ModelViewSet):
    serializer_class = ListingSerializer
    queryset = Listing.objects.all()

    def get_queryset(self):
        channel_id = self.request.GET.get("channel_id", None)
        if channel_id:
            try:
                channel = Channel.objects.get(id=channel_id)
                if channel:
                    return channel.listings.all()
            except Exception as e:
                print(e)
                return []
        return super().get_queryset()
    
    

        
class ProductView(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        product = get_object_or_404(Product, pk=pk)
        channel = ChannelSerializer(product.channel).data
        reviews = ReviewSerializer(Review.objects.filter(product=product), many=True).data
        questions = QuestionSerializer(Question.objects.filter(product=product), many=True).data
        return Response({
            "product": ProductSerializer(product).data,
            "channel": channel,
            "reviews": reviews,
            "questions": questions
        })
        

    def get_queryset(self):
        channel_id = self.request.GET.get("channel_id")
        offset = int(self.request.GET.get("offset", 0))
        limit = int(self.request.GET.get('limit', 10))
        try:
            channel = Channel.objects.get(id=channel_id)
            if channel:
                return channel.products.all()
        except Exception as e:
            print(e)
        return Product.objects.all()
    
    

class ReviewView(ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

class QuestionView(ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

class AnswerView(ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
