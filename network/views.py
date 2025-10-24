from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from .models import User, Post, Comment
# Importe UserUpdateSerializer para que o get_serializer_class funcione
from .serializers import UserSerializer, PostSerializer, CommentSerializer, UserUpdateSerializer 

User = get_user_model()

# Permissão customizada: Leitura aberta, edição só para o dono
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj == request.user

# Views para Usuários
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
    # MUDANÇA AQUI: Troca o serializador se for PUT ou PATCH
    def get_serializer_class(self):
        # Se o método for de escrita (PATCH/PUT), usa o serializador restrito
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        
        # Para leitura (GET) e outros, usa o serializador padrão (completo)
        return self.serializer_class

    def patch(self, request, *args, **kwargs):
        # partial=True garante que o UserUpdateSerializer só precise de 'bio' ou 'password'
        return self.update(request, partial=True)
        
    def put(self, request, *args, **kwargs):
        return Response({'error': 'PUT não suportado. Use PATCH para atualizações parciais.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@extend_schema(
    methods=['post'],
    request=None,
    responses={
        200: OpenApiResponse(description='Seguindo com sucesso', response={'type': 'object', 'properties': {'message': {'type': 'string'}}}),
        404: OpenApiResponse(description='Usuário não encontrado', response={'type': 'object', 'properties': {'error': {'type': 'string'}}})
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    try:
        user_to_follow = User.objects.get(id=user_id)
        request.user.following.add(user_to_follow)
        return Response({'message': 'Seguindo!'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

@extend_schema(
    methods=['post'],
    request=None,
    responses={
        200: OpenApiResponse(description='Deixou de seguir com sucesso', response={'type': 'object', 'properties': {'message': {'type': 'string'}}}),
        404: OpenApiResponse(description='Usuário não encontrado', response={'type': 'object', 'properties': {'error': {'type': 'string'}}})
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, user_id):
    try:
        user_to_unfollow = User.objects.get(id=user_id)
        request.user.following.remove(user_to_unfollow)
        return Response({'message': 'Deixou de seguir!'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

# Views para Posts
class PostList(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(
    methods=['post'],
    request=None,
    responses={
        200: OpenApiResponse(description='Curtiu ou descurtida', response={'type': 'object', 'properties': {'message': {'type': 'string'}}}),
        404: OpenApiResponse(description='Post não encontrado', response={'type': 'object', 'properties': {'error': {'type': 'string'}}})
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response({'message': 'Curtiu cancelada!'}, status=status.HTTP_200_OK)
        else:
            post.likes.add(request.user)
            return Response({'message': 'Curtiu!'}, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({'error': 'Post não encontrado'}, status=status.HTTP_404_NOT_FOUND)

# View para Comentários
class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = Post.objects.get(id=post_id)
        serializer.context['post'] = post
        serializer.save(author=self.request.user)

# Feed
class FeedList(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following = self.request.user.following.all()
        return Post.objects.filter(author__in=following).order_by('-created_at')