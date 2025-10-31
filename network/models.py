from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = CloudinaryField(
        'image', 
        folder='profile_pics/',
        blank=True, 
        null=True,
        transformation=[{'width': 300, 'height': 300, 'crop': 'fill', 'gravity': 'auto'}]
    )
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        app_label = 'network'

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comentário de {self.author.username} no post {self.post.id}'
    
class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')  # Relaciona com User
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Pra ordenar por atividade recente

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversa {self.id} - {', '.join([p.username for p in self.participants.all()[:2]])}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Pra notificações (futuro)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg de {self.author.username}: {self.content[:50]}"