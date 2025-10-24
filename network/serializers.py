from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.contrib.auth import get_user_model
from .models import User, Post, Comment

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'bio', 'followers_count', 'following_count']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        # NOTA: O tratamento de restrição de campos agora será feito via 
        # UserUpdateSerializer.read_only_fields.
        
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Chama a implementação padrão para aplicar os campos restantes (como 'bio')
        instance = super().update(instance, validated_data) 
        
        # Salva o objeto (necessário se a senha foi alterada)
        instance.save()
        return instance

    @extend_schema_field(int)
    def get_followers_count(self, obj) -> int:
        return obj.followers.count()

    @extend_schema_field(int)
    def get_following_count(self, obj) -> int:
        return obj.following.count()

# NOVO SERIALIZER DEDICADO PARA ATUALIZAÇÃO (PATCH)
class UserUpdateSerializer(UserSerializer):
    """
    Serializador para atualizar perfil (PATCH). Torna username e email read-only.
    """
    class Meta(UserSerializer.Meta):
        read_only_fields = ('username', 'email', 'followers_count', 'following_count')
        # Mantém 'bio' e 'password' editáveis. O 'update' será herdado do UserSerializer.

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
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'post', 'author', 'created_at']

    def create(self, validated_data):
        # O contexto deve ser preenchido pela View (CommentListCreateAPIView)
        validated_data['post'] = self.context['post']
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)