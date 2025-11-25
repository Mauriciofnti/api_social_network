from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth import get_user_model
from .models import User, Post, Comment, Conversation, Message

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
            print("Erro no update:", str(e))
            raise

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'post', 'author', 'created_at']

    def create(self, validated_data):
        validated_data['post'] = self.context['post']
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    
class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    user_has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'likes_count', 'comments', 'user_has_liked']

    @extend_schema_field(int)
    def get_likes_count(self, obj) -> int:
        return obj.likes.count()

    def get_user_has_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False

class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'author', 'content', 'created_at', 'is_read']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'updated_at', 'messages', 'last_message']

    @extend_schema_field({'type': 'object'})
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        return MessageSerializer(last_msg).data if last_msg else None

class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content']

    def create(self, validated_data):
        conversation = self.context['conversation']
        validated_data['conversation'] = conversation
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)