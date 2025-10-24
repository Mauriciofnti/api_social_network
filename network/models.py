from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')  # Liga ao post
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')  # Quem comentou
    content = models.TextField(max_length=500)  # Texto do comentário
    created_at = models.DateTimeField(auto_now_add=True)  # Data auto

    class Meta:
        ordering = ['-created_at']  # Mais novos primeiro

    def __str__(self):
        return f'Comentário de {self.author.username} no post {self.post.id}'