from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Channel(models.Model):
    name = models.CharField(max_length=100)
    photo = models.URLField(null=True, blank=True)
    cat = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    time_open = models.TextField(null=True, blank=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

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

    def __str__(self):
        return self.name

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
        return f"{self.username} - {self.product.name} - {self.body} "


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
