from django.urls import path
from .views import (
    UserList, UserDetail, follow_user, unfollow_user,
    PostList, PostDetail, like_post, FeedList, CommentListCreateAPIView
)

urlpatterns = [
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    path('users/<int:user_id>/follow/', follow_user, name='follow-user'),
    path('users/<int:user_id>/unfollow/', unfollow_user, name='unfollow-user'),
    
    path('posts/', PostList.as_view(), name='post-list'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/', like_post, name='like-post'),
    path('posts/<int:post_id>/comments/', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    
    path('feed/', FeedList.as_view(), name='feed'),
]