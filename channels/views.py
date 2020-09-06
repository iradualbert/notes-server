import json
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
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

http_errors = {
    "afd": Response({"detail": "Authentication credentials were not provided."}, status=401),
    "400": Response({'detail': 'Invalid'}, status=400),
    "404": Response({'detail': 'Not found'}, status=404),
    "403": Response({'detail': 'Forbidden'})

}


class ChannelView(ModelViewSet):
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()

class SubscriptionView(ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    def update(self, request, *args, **kwargs):
        return Response({'detail': 'not allowed'}, status=403)
    

    def create(self, request, *args, **kwargs):
        user = request.user
        channel_id = request.GET.get('channel_id')
        data = json.loads(request.body)
        channel= get_object_or_404(Channel, pk=channel_id)
        serializer = SubscriptionSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user, channel=channel)
            return Response({'status': 'subscribed'})
        else:
            return Response(serializer.errors, status=400)


    def destroy(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get('pk')
        sub = get_object_or_404(Subscription, pk=pk)
        if sub.user == user:
            sub.delete()
        else:
            return Response({'status': 'bad request'}, status=400)


    

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
   # permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "detail": "Authentication credentials were not provided.",
            }, status=401)
        product_id = request.GET.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        data = json.loads(request.body)
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            review = serializer.save(user=user, product=product)
            return Response(review.data, status=201)
        else:
            return Response(serializer.errors, status=400)
    
    def list(self, request, *args, **kwargs):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 5))
        product_id = request.GET.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
                to_fetch = limit + 1
                fetched = Review.objects.filter(product=product)[offset:to_fetch]
                more_available = len(fetched) == to_fetch
                results = fetched[0:limit]
                return Response({
                    'reviews': ReviewSerializer(results, many=True).data,
                    'more_available': more_available
                })
            except ObjectDoesNotExist:
                pass
        return super().list(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get('pk')
        review = get_object_or_404(Review, pk=pk)
        if not user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        if review.user !=user:
            return Response({'detail': 'Forbidden'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get('pk')
        if user.is_authenticated and pk:
            review = get_object_or_404(Review, pk=pk)
            if review.user == user:
                review.delete();
                return Response({'status': 'ok'})
        return Response({'detail': 'invalid request'}, status=400)



class QuestionView(ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return Response({
                "detail": "Authentication credentials were not provided.",
            }, status=401)
        product_id = request.GET.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        data = json.loads(request.body)
        serializer = QuestionSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            question = serializer.save(user=user, product=product)
            return Response(question.data, status=201)
        else:
            return Response(serializer.errors, status=400)
    
    def list(self, request, *args, **kwargs):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 5))
        product_id = request.GET.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(pk=product_id)
                to_fetch = limit + 1
                fetched = Question.objects.filter(product=product)[offset:to_fetch]
                more_available = len(fetched) == to_fetch
                results = fetched[0:limit]
                return Response({
                    'questions': QuestionSerializer(results, many=True).data,
                    'more_available': more_available
                })
            except ObjectDoesNotExist:
                pass
        return super().list(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get('pk')
        question = get_object_or_404(Question, pk=pk)
        if not user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        if question.user !=user:
            return Response({'detail': 'Forbidden'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
     
        return Response({'detail': 'question are not editable'}, status=400)
    


class AnswerView(ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        question_id = request.GET.get('question_id')
        question = get_object_or_404(Question, pk=question_id)
        data = json.loads(request.body)
        if not user.is_authenticated:
            return Response({'detail': 'Authentication Credentials were not provided'}, status=401)
        channel = question.product.channel
        if channel.can_answer(user):
            serializer = AnswerSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(question=question, user=user)
            else:
                return Response(serializer.errors, status=400)
        else:
            return Response({'detail': 'bad request'}, status=400)
    
    def destroy(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        if user.is_authenticated:
            answer = get_object_or_404(Answer, pk=pk)
            if answer.user == user:
                answer.delete()
            else:
                return Response({'detail': 'bad request'})
        
        else:
            return Response({'detail': 'Authentication credentials were not provided'}, status=401)
    
    def update(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get('pk')
        answer = get_object_or_404(Answer, pk=pk)
        if not user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        if answer.user != user:
            return Response({'detail': 'Forbidden'}, status=403)
        return super().update(request, *args, **kwargs)
