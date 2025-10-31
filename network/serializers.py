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

# SERIALIZER PARA ATUALIZAÇÃO (PATCH) - AJUSTE: Fields explícitos pra bio/password only
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

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'likes_count', 'comments']

    @extend_schema_field(int)
    def get_likes_count(self, obj) -> int:
        return obj.likes.count()

# NOVOS SERIALIZERS PARA DMS
class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # Nested pra mostrar quem enviou

    class Meta:
        model = Message
        fields = ['id', 'author', 'content', 'created_at', 'is_read']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)  # Array de users na conversa
    messages = MessageSerializer(many=True, read_only=True)  # Array de msgs (limite se precisar)
    last_message = serializers.SerializerMethodField()  # Preview da última msg

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