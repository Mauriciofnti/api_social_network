from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .models import User, Post
from .serializers import UserSerializer, PostSerializer

User = get_user_model()

# Views para Usuários
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Qualquer um pode listar/criar

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Qualquer um pode ver perfil

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    try:
        user_to_follow = User.objects.get(id=user_id)
        request.user.following.add(user_to_follow)
        return Response({'message': 'Seguindo!'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

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
        return Post.objects.filter(author=self.request.user)  # Só meus posts

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # Autor é o usuário logado

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # Logado pode ver/editar/deletar

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

# Feed: Posts de quem eu sigo
class FeedList(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following = self.request.user.following.all()
        return Post.objects.filter(author__in=following).order_by('-created_at')