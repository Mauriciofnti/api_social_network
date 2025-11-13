from rest_framework import generics, status
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import check_password
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import User, Post, Comment, Message, Conversation
from .serializers import UserSerializer, PostSerializer, CommentSerializer, UserUpdateSerializer, ConversationSerializer, CreateMessageSerializer 

User = get_user_model()

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

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("username")  # o front envia o e-mail neste campo
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Senha incorreta")

        attrs["username"] = user.username  # força o JWT a reconhecer o usuário
        data = super().validate(attrs)
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer        

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
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        print("🟡 Dados recebidos no POST /api/users/:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("🔴 Erros de validação:", serializer.errors)  # 👈 adiciona esta linha
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        print("🟢 Usuário criado com sucesso:", serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
    
# ... todo o código existente até FeedList ...

# NOVAS VIEWS PARA DMS
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
        # Valida ID
        target_user_id = int(target_user_id)
        if target_user_id <= 0:
            return Response({'error': 'ID de usuário inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        target_user = get_object_or_404(User, id=target_user_id)  # 404 auto se não existir
        
        if request.user.id == target_user.id:
            return Response({'error': 'Não pode iniciar conversa consigo mesmo'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se já existe conversa (query safe com logs)
        try:
            conversation = Conversation.objects.filter(
                participants=request.user
            ).filter(
                participants=target_user
            ).first()
            print(f"DEBUG DM: Query result - Conversation exists: {conversation is not None}")  # Log pra debug
        except Exception as query_err:
            print(f"DEBUG DM: Erro na query M2M: {query_err}")  # Log erro específico
            return Response({'error': 'Erro ao verificar conversa existente'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, target_user)
            conversation.save()
            print(f"DEBUG DM: Nova conversa criada ID {conversation.id}")  # Log

        # Serializer com safe context
        try:
            serializer = ConversationSerializer(conversation)
        except Exception as ser_err:
            print(f"DEBUG DM: Erro no serializer: {ser_err}")
            return Response({'error': 'Erro ao processar conversa'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({'error': 'ID de usuário inválido'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"DEBUG DM: Erro inesperado: {e}")  # Log geral
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
        print(f"DEBUG DM SEND: Conv ID {conversation_id} encontrada, participants: {conversation.participants.count()}")  # Log pra debug
        
        if request.user not in conversation.participants.all():
            return Response({'error': 'Você não faz parte dessa conversa'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreateMessageSerializer(data=request.data, context={
            'request': request,
            'conversation': conversation
        })
        if serializer.is_valid():
            message = serializer.save()
            # Atualiza timestamp da conversa
            conversation.updated_at = message.created_at
            conversation.save()
            print(f"DEBUG DM SEND: Msg enviada ID {message.id} em conv {conversation_id}")  # Log sucesso
            return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Conversation.DoesNotExist:
        print(f"DEBUG DM SEND: Conv ID {conversation_id} não existe")  # Log específico
        return Response({'error': 'Conversa não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"DEBUG DM SEND: Erro inesperado: {e}")  # Log geral
        return Response({'error': 'Erro interno ao enviar mensagem'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# View pra listar conversas do user (adicione se quiser feed de DMs)
@extend_schema(responses={200: ConversationSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_conversations(request):
    conversations = request.user.conversations.all()
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)

@extend_schema(
    responses={200: ConversationSerializer()}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation(request, conversation_id):
    """
    Retorna detalhes de uma conversa específica (msgs, participants).
    """
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if request.user not in conversation.participants.all():
            return Response({'error': 'Você não faz parte dessa conversa'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"DEBUG DM GET: Erro: {e}")  # Log pra debug
        return Response({'error': 'Erro ao carregar conversa'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)