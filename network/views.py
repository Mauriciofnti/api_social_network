from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.db.models import Prefetch
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import User, Post, Comment, Message, Conversation
from .serializers import UserSerializer, PostSerializer, CommentSerializer, UserUpdateSerializer, ConversationSerializer, CreateMessageSerializer 

User = get_user_model()

class CustomTokenObtainPairView(GenericAPIView):
    serializer_class = TokenObtainPairSerializer
    permission_classes = [AllowAny]

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
        
        return Response(response_data, status=status.HTTP_200_OK)

class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Handles retrieval and update of the authenticated user's profile.
    Supports partial updates (PATCH) including profile picture uploads.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
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

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj == request.user

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
            request.user.save()
            message = 'Deixou de seguir!'
        else:
            request.user.following.add(user_to_toggle)
            request.user.save()
            message = 'Seguindo!'

        new_followers_count = user_to_toggle.followers.count()
        current_user_following_count = request.user.following.count()

        return Response({
            'message': message,
            'is_following': not is_following,
            'followers_count': new_followers_count, 
            'following_count': current_user_following_count,
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)


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
        200: OpenApiResponse(
            description='Curtiu ou descurtida com count atualizado', 
            response={
                'type': 'object', 
                'properties': {
                    'message': {'type': 'string'},
                    'likes_count': {'type': 'integer'},
                    'user_has_liked': {'type': 'boolean'}
                }
            }
        ),
        404: OpenApiResponse(description='Post não encontrado', response={'type': 'object', 'properties': {'error': {'type': 'string'}}}),
        400: OpenApiResponse(description='Erro na curtir', response={'type': 'object', 'properties': {'error': {'type': 'string'}}}),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        
        if user in post.likes.all():
            post.likes.remove(user)
            has_liked = False
            message = 'Curtiu cancelada!'
        else:
            post.likes.add(user)
            has_liked = True
            message = 'Curtiu!'
        
        likes_count = post.likes.count()
        
        serializer_context = {'request': request}
        
        return Response({
            'message': message,
            'likes_count': likes_count,
            'user_has_liked': has_liked
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Erro ao processar like: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    

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

class FeedList(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following_users = list(self.request.user.following.all())
        authors = [self.request.user] + following_users 
        
        return Post.objects.filter(
            author__in=authors
        ).select_related('author').prefetch_related(
            Prefetch('likes'),  # Likes do post
            Prefetch('comments', queryset=Comment.objects.select_related('author'))
        ).order_by('-created_at')
    
@extend_schema(
    methods=['post'],
    request={'type': 'object', 'properties': {'target_user_id': {'type': 'integer'}}},
    responses={
        201: OpenApiResponse(description='Conversa criada/iniciada'),
        400: OpenApiResponse(description='Erro (ex: mesmo usuário)'),
        404: OpenApiResponse(description='Usuário não encontrado'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request, target_user_id):
    try:
        try:
            target_user_id = int(target_user_id)
        except ValueError:
            return Response({'error': 'ID de usuário inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        if target_user_id <= 0:
            return Response({'error': 'ID de usuário inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        target_user = get_object_or_404(User, id=target_user_id)
        
        if request.user.id == target_user.id:
            return Response({'error': 'Não pode iniciar conversa consigo mesmo'}, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=target_user
        ).first()

        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, target_user)
            conversation.save()

        serializer = ConversationSerializer(conversation, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': f'Erro interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@extend_schema(
    methods=['post'],
    request={'type': 'object', 'properties': {'content': {'type': 'string'}}},
    responses={
        201: OpenApiResponse(description='Mensagem enviada'),
        403: OpenApiResponse(description='Não autorizado na conversa'),
        404: OpenApiResponse(description='Conversa não encontrada'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, conversation_id):
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in conversation.participants.all():
            return Response({'error': 'Você não faz parte dessa conversa'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateMessageSerializer(data=request.data, context={
            'request': request,
            'conversation': conversation
        })
        if serializer.is_valid():
            message = serializer.save()
            conversation.updated_at = message.created_at
            conversation.save()
            return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Erro interno ao enviar mensagem'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@extend_schema(responses={200: ConversationSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_conversations(request):
    conversations = request.user.conversations.all().order_by('-updated_at')
    serializer = ConversationSerializer(conversations, many=True, context={'request': request})
    return Response(serializer.data)

@extend_schema(
    responses={200: ConversationSerializer()}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation(request, conversation_id):
    """
    Retorna detalhes de uma conversa específica (msgs, participants).
    Suporta paginação: ?page=1&limit=20 pra mensagens.
    """
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return Response({'error': 'Você não faz parte dessa conversa'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ConversationSerializer(conversation, context={
            'request': request,
            'page': request.query_params.get('page', 1),
            'limit': request.query_params.get('limit', 20)
        })
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Erro ao carregar conversa'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)