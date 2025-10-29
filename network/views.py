from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from .models import User, Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer, UserUpdateSerializer 

User = get_user_model()

# SEÇÃO DE AUTENTICAÇÃO (JWT) - VERSÃO LIMPA E ÚNICA
class CustomTokenObtainPairView(GenericAPIView):
    serializer_class = TokenObtainPairSerializer
    permission_classes = [AllowAny]  # Público pra login

    @extend_schema(
        request=serializer_class,
        responses={
            200: OpenApiResponse(
                description='Login bem-sucedido',
                response={
                    'type': 'object',
                    'properties': {
                        'access': {'type': 'string'},
                        'refresh': {'type': 'string'},
                        'user': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'username': {'type': 'string'},
                                'email': {'type': 'string'}
                            }
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description='Credenciais inválidas',
                response={'type': 'object', 'properties': {'non_field_errors': {'type': 'array'}}}
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.user
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }
        
        # print(f"DEBUG LOGIN: Enviando user: {user.username} (ID: {user.id})")
        
        return Response(response_data, status=status.HTTP_200_OK)

# View pra user atual (me) - Suporta GET e PATCH pra editar perfil
class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Handles retrieval and update of the authenticated user's profile.
    Supports partial updates (PATCH) including profile picture uploads.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Permite upload via form-data

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer  # Serializer restrito pra update (bio/password/profile_picture)
        return self.serializer_class

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def patch(self, request, *args, **kwargs):
        return self.update(request, partial=True)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data['message'] = 'Perfil atualizado com sucesso!'
        return response

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
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return self.serializer_class

    def patch(self, request, *args, **kwargs):
        return self.update(request, partial=True)
        
    def put(self, request, *args, **kwargs):
        return Response({'error': 'PUT não suportado. Use PATCH para atualizações parciais.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# GET status de follow pra inicializar botão no frontend
@extend_schema(
    methods=['get'],
    responses={
        200: OpenApiResponse(
            description='Status de follow', 
            response={'type': 'object', 'properties': {'is_following': {'type': 'boolean'}}}
        ),
    }
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_follow_status(request, user_id):
    try:
        user_to_check = User.objects.get(id=user_id)
        if request.user.id == user_to_check.id:
            return Response({'error': 'Não aplica pra si mesmo'}, status=status.HTTP_400_BAD_REQUEST)
            
        is_following = user_to_check in request.user.following.all()
        
        return Response({'is_following': is_following}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
@extend_schema(
    methods=['post'],
    request=None,
    responses={
        200: OpenApiResponse(
            description='Toggle follow/unfollow com sucesso', 
            response={
                'type': 'object', 
                'properties': {
                    'message': {'type': 'string'},
                    'is_following': {'type': 'boolean'},
                    'followers_count': {'type': 'integer'},
                    'following_count': {'type': 'integer'},
                }
            }
        ),
        404: OpenApiResponse(description='Usuário não encontrado', response={'type': 'object', 'properties': {'error': {'type': 'string'}}}),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_follow_user(request, user_id):
    try:
        user_to_toggle = User.objects.get(id=user_id)
        if request.user.id == user_to_toggle.id:
            return Response({'error': 'Não pode seguir a si mesmo'}, status=status.HTTP_400_BAD_REQUEST)

        is_following = user_to_toggle in request.user.following.all()
        
        if is_following:
            request.user.following.remove(user_to_toggle)
            request.user.save()  # Salva o usuário logado
            message = 'Deixou de seguir!'
        else:
            request.user.following.add(user_to_toggle)
            request.user.save()
            message = 'Seguindo!'

        new_followers_count = user_to_toggle.followers.count()  # Seguidores do ALVO (perfil visto)
        current_user_following_count = request.user.following.count()  # Seguindo do USUÁRIO LOGADO

        return Response({
            'message': message,
            'is_following': not is_following,
            'followers_count': new_followers_count,  # Para atualizar no ProfileView (alvo)
            'following_count': current_user_following_count,  # Para atualizar no store do logado
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
# Views para Posts
class PostList(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        author_id = self.request.query_params.get('author')
        if author_id:
            return Post.objects.filter(author_id=author_id).order_by('-created_at')
        return Post.objects.filter(author=self.request.user).order_by('-created_at')

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
        404: OpenApiResponse(description='Post não encontrado', response={'type': 'object', 'properties': {'error': {'type': 'string'}}}),
        400: OpenApiResponse(description='Erro na curtir', response={'type': 'object', 'properties': {'error': {'type': 'string'}}}),
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
        # Posts do usuário logado (sempre incluídos)
        own_posts = Post.objects.filter(author=self.request.user)
        
        # Posts dos followed (se existir)
        following = self.request.user.following.all()
        if following.exists():
            followed_posts = Post.objects.filter(author__in=following)
            return (followed_posts | own_posts).order_by('-created_at') 
        return own_posts.order_by('-created_at')