import json
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
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
    LinkSerializer
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
    Answer,
    Link
)
from .utils import get_ip_address

http_errors = {
    "afd": Response({"detail": "Authentication credentials were not provided."}, status=401),
    "400": Response({'detail': 'Invalid'}, status=400),
    "404": Response({'detail': 'Not found'}, status=404),
    "403": Response({'detail': 'Forbidden'})

}


class ChannelView(ModelViewSet):
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get('pk')
        channel = get_object_or_404(Channel, pk=pk)
        channel_json_data = ChannelSerializer(channel).data
        channel_json_data['is_subscribed'] = channel.is_subscribed(user)
        return Response(channel_json_data, status=200)

    def list(self, request, *args, **kwargs):
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 8))
        to_fetch = limit + 1
        user_location = request.GET.get('user_location', {})
        user = request.user
        if not user_location and user.is_authenticated:
            lat = user.profile.lat
            lng = user.profile.lng
        user_ip_address = get_ip_address(request)
        fetched = Channel.objects.all()[offset: offset + to_fetch]
        more_available = len(fetched) == to_fetch
        results = ChannelSerializer(fetched[0:limit], many=True).data
        return JsonResponse({
            "channels": results,
            "more_available": more_available
        })
    
    def create(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile
        data = json.loads(request.body)
        serializer = ChannelSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user)
            profile.has_channel = True
            profile.use_channel = True
            profile.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
    @staticmethod
    @api_view(['GET'])
    def about(request, channel_id):
        channel = get_object_or_404(Channel, pk=channel_id)
        links = channel.links
        link_data = LinkSerializer(links, many=True).data
        return Response({
            "links": link_data
        }, status=200)

    @staticmethod
    @api_view(['POST', 'UPDATE'])
    def add_link(request, channel_id):
        user = request.user
        channel = get_object_or_404(Channel, pk=channel_id)
        if not user.is_authenticated or user != channel.user:
            return Response({'detail': 'not authenticated'}, status=401)
        data = request.data
        id = data.get('id')
        if id is not None:
            link = get_object_or_404(Link, pk=id)
            if link.channel == channel:
                serializer = LinkSerializer(link, data)
                if not serializer.is_valid(raise_exception=True):
                    return Response(serializer.errors, status=400)
                serializer.save()
                return Response({'status': 'ok'}, 201)
            else:
                return Resonse({'detail': 'forbidden'}, status=403)
        serializer = LinkSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(channel=channel)
            return Response({'status': 'ok'}, status=201)
        else:
            return Response(serializer.errors, status=400)
    
    @staticmethod
    @api_view(['DELETE'])
    def destroy_link(request, link_id):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'not authenticated'}, status=401)
        link = get_object_or_404(Link, pk=link_id)
        if user != link.channel.user:
            return Response({'detail': 'forbiden'}, status=403)
        else:
            link.delete()
            return Response({'status': 'ok'}, status=203)


    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        try:
            channel = Channel.objects.get(pk=pk)
            if channel.user == user:
                return super().update(request, *args, **kwargs)
        except ObjectDoesNotExist:
            pass
        return JsonResponse({'detail': 'invalid request'}, status=403)
    
    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = request.user
        try:
            channel = Channel.objects.get(pk=pk)
            if channel.user == user:
                return super().destroy(request, *args, **kwargs)
        except ObjectDoesNotExist:
            pass
        return JsonResponse({'detail': 'forbidden'}, status=403)


class SubscriptionView(ModelViewSet):
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    def update(self, request, *args, **kwargs):
        return Response({'detail': 'uneditable'}, status=400)
    def list(self, request, *args, **kwargs):
        return Response({'detail': 'invalid request'}, status=400)

    def retrieve(self, *args, **kwargs):
        return Response({'detail': 'invalid request'}, status=400)
    

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
            return Response({'detail': 'bad request'}, status=400)


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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        product = get_object_or_404(Product, pk=pk)
        channel = product.channel
        channel_json_data = ChannelSerializer(channel).data
        user = request.user
        if user.is_authenticated:
            product.add_view(user)
            channel_json_data['is_subscribed'] = channel.is_subscribed(user)
            
        # reviews = ReviewSerializer(Review.objects.filter(product=product)[0:6], many=True).data
        # questions = QuestionSerializer(Question.objects.filter(product=product)[0:6], many=True).data
        reviews = ReviewSerializer(Review.objects.all(), many=True).data
        questions = QuestionSerializer(Question.objects.all(), many=True).data
        return Response({
            "product": ProductSerializer(product).data,
            "channel": channel_json_data,
            "reviews": reviews,
            "questions": questions
        })
    
    def list(self, request, *args, **kwargs):
        channel_id = request.GET.get("channel_id")
        offset = int(request.GET.get("offset", 0))
        limit = int(request.GET.get('limit', 10))
        to_fetch = limit + 1
        fetched = []
        more_available = False
        if channel_id:
            try:
                channel = Channel.objects.get(id=channel_id)
                if channel:
                    fetched = channel.products.all()[offset:offset+to_fetch]
                    more_available = len(fetched) == to_fetch
            except ObjectDoesNotExist:
                return JsonResponse({'detail': 'not found'}, status=404)
        else:
            fetched = Product.objects.all()[offset: offset + to_fetch]
            more_available = len(fetched) == to_fetch
        
        results = ProductSerializer(fetched[0:limit], many=True).data
        return JsonResponse({
            "products": results,
            "more_available": more_available
        })

    def create(self, request, *args, **kwargs):
        user = request.user
        data = json.loads(request.body)
        try:
            channel = user.channel
        except ObjectDoesNotExist:
            profile = user.profile
            channel = Channel.objects.create(
                name=user.first_name,
                address = profile.address,
                lat=profile.lat,          
                lng=profile.lng,
                user=user     
                )
            profile.has_channel = True
            profile.use_channel = True
            profile.save()   
        serializer = ProductSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(channel=channel)
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=403)
    def update(self, request, *args, **kwargs):
        return JsonResponse({'detail': "You can't change product data once created"}, status=403)
    
    def destroy(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get('pk')
        try:
            product = Product.objects.get(pk=pk)
            if product and product.user == user:
                return super().destroy(request, *args, **kwargs)
        except:
            return JsonResponse({'detail': 'forbidden request'}, status=403)

class ReviewView(ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        user = request.user
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
        if review.user !=user:
            return Response({'detail': 'Forbidden'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get('pk')
        if pk:
            review = get_object_or_404(Review, pk=pk)
            if review.user == user:
                review.delete()
                return Response({'status': 'ok'})
        return Response({'detail': 'invalid request'}, status=400)



class QuestionView(ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def create(self, request, *args, **kwargs):
        user = request.user
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
        if question.user !=user:
            return Response({'detail': 'Forbidden'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'question are not editable'}, status=403)
    


class AnswerView(ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )

    def create(self, request, *args, **kwargs):
        user = request.user
        question_id = request.GET.get('question_id')
        question = get_object_or_404(Question, pk=question_id)
        data = json.loads(request.body)
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
        answer = get_object_or_404(Answer, pk=pk)
        if answer.user == user:
            answer.delete()
        else:
            return Response({'detail': 'bad request'})
    
    def update(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get('pk')
        answer = get_object_or_404(Answer, pk=pk)
        if answer.user != user:
            return Response({'detail': 'Forbidden'}, status=403)
        return super().update(request, *args, **kwargs)