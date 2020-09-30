from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos.point import Point
from django.db.models import Q
from django.contrib.gis.measure import D
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_delete, pre_save, post_save
# Create your models here.

class Channel(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.URLField(null=True, blank=True)
    cat = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    website = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    time_open = models.TextField(null=True, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    geom = models.PointField(srid=4326, null=True)
    created_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    
    def can_answer(self, user):
        if user == self.user:
            return True
        return False

    def get_similar_channels(self):
        return []

    def get_nearby(self, offset=0, limit=6, m=2500, similar_cat=False):
        if self.geom:
            to_fetch = limit + 1
            fetched = []
            if similar_cat:
                fetched = Channel.objects.filter(
                    Q(geom__distance_lt=(self.geom, D(m=m))),
                    cat=self.cat
                    ).exclude(
                        pk=self.pk
                        )[offset: to_fetch+limit]
            else:
                fetched = Channel.objects.filter(
                    Q(geom__distance_lt=(self.geom, D(m=m)))
                    ).exclude(
                        pk=self.pk
                        )[offset: to_fetch+limit]
            more_available = len(fetched) == to_fetch
            return fetched[0:limit], more_available
        return [], False

    def save(self, *args, **kwargs):
        if(self.lat and self.lng):
            self.geom = Point([float(x) for x in (self.lng, self.lat)], srid=4326)
        super(self.__class__, self).save(*args, **kwargs)

class Branch(models.Model):
    main_channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="branches")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="connections")
    permission = models.CharField(max_length=100)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['channel', 'main_channel']]

class ChannelAdmin(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="admins")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="connections")
    user_role = models.CharField(max_length=100)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)

class Product(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    photo = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    link = models.URLField(blank=True, null=True)
    link_type = models.TextField(blank=True, null=True)
    price = models.TextField(blank=True, null=True)
    listing = models.ForeignKey('Listing', on_delete=models.SET_NULL, related_name="products", null=True, blank=True)
    cat = models.TextField(blank=True) # cat stands for category
    # rates and reviews
    average_rate  = models.FloatField(null=True, blank=True, default=0)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    total_views = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    def similar_products(self):
        pass

    def add_view(self, user):
        obj, created = View.objects.get_or_create(
            user=user,
            product=self
        )
        if created:
            self.views +=1 
            self.save()
        else:
            obj.last_time_viewed = datetime.now()
            obj.save()
        

class View(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="viewed")
    time_viewed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_time_viewed = models.DateField(default=datetime.now)

    class Meta:
        unique_together = [['user', 'product']]

class Listing(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="listings")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    body = models.CharField(max_length=500)
    rate = models.FloatField()
    likes = models.ManyToManyField(User, blank=True, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['product', 'user']]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.body} "


class Question(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name="questions",
                             null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="asked")
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers")
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.answer


class Subscription(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="subscribers")
    notify = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'channel']]


@receiver(pre_delete, sender=Review)
def _review_delete(sender, instance, **kwargs):
    product = instance.product
    if product.total_reviews > 1:
        product.average_rate = (
            (product.average_rate * product.total_reviews) - instance.rate) / (product.total_reviews - 1)
        product.total_reviews = product.total_reviews - 1

    else:
        product.total_reviews = 0
        product.average_rate = 0
    product.save()


@receiver(pre_save, sender=Review)
def review_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Review.objects.get(pk=instance.pk)
    except:
        instance._pre_save_instance = instance

@receiver(post_save, sender=Review)
def _review_create(sender, instance, created,**kwargs):
    product = instance.product
    if created:
         product.average_rate = (
             (product.average_rate * product.total_reviews) + instance.rate) / (product.total_reviews + 1)
         product.total_reviews = product.total_reviews + 1
    else:
        product.average_rate = (
            (product.average_rate * product.total_reviews) + instance.rate - instance._pre_save_instance.rate) / (product.total_reviews)
    product.save()
