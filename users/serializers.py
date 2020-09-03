from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib.auth import authenticate

# user Serializer
class UserSerializer(serializers.ModelSerializer):
    fullname=serializers.CharField(source="first_name")
    #photo=serializers.ImageField(source="profile.photo")
    class Meta:
        model = User
        fields = ('username', 'email', 'fullname')


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name')
        extra_kwargs = {'password': {'write_only': True},
                         'first_name': {'required': False},
                        'email': {'required': True,
                                  'validators': [UniqueValidator(User.objects.all(), f'A user with that Email already exists.')]},
                        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name']
        )
        return user

# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user 
        raise serializers.ValidationError('Incorrect Credentials')