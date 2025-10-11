from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Post
from .serializers import UserSerializer, PostSerializer

User = get_user_model()

class UserSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='123456')

    def test_user_serializer(self):
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['followers_count'], 0)

class PostAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='123456')
        # Crie token JWT para autenticação API
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')  # Define header global no client

    def test_create_post(self):
        response = self.client.post('/api/posts/', {'content': 'Test post!'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)

    def test_list_posts(self):
        Post.objects.create(author=self.user, content='Post 1')
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)