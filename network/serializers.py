from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth import get_user_model
from .models import User, Post, Comment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    profile_picture = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_picture', 'password', 'bio', 'followers_count', 'following_count']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        instance = super().update(instance, validated_data) 
        instance.save()
        return instance

    @extend_schema_field(int)
    def get_followers_count(self, obj) -> int:
        return obj.followers.count()

    @extend_schema_field(int)
    def get_following_count(self, obj) -> int:
        return obj.following.count()

class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture', 'password', 'bio']
        extra_kwargs = {
            'profile_picture': {'required': False},
            'email': {'required': False},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        try:
            updated_instance = super().update(instance, validated_data)
            updated_instance.save()
            return updated_instance
        except Exception as e:
            # Log erro para debug
            print("Erro no update:", str(e))
            raise  # Re-raise para 500 virar 400 com detalhe

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'likes_count']

    @extend_schema_field(int)
    def get_likes_count(self, obj) -> int:
        return obj.likes.count()

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']  # ← AJUSTE: 'content' em vez de 'text' se model usar content
        read_only_fields = ['id', 'post', 'author', 'created_at']

    def create(self, validated_data):
        validated_data['post'] = self.context['post']
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)