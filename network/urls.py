from django.urls import path
from .views import (
    CustomTokenObtainPairView, CurrentUserView, UserList, UserDetail,
    PostList, PostDetail, FeedList, CommentListCreateAPIView,
    toggle_follow_user, get_follow_status, like_post
)  # Removidos follow/unfollow se não usar mais

urlpatterns = [
    # Auth
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/me/', CurrentUserView.as_view(), name='current_user'),
    
    # Users
    path('users/', UserList.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user_detail'),
    # path('users/<int:user_id>/follow/', follow_user, name='follow_user'),  # Comentado, use toggle
    # path('users/<int:user_id>/unfollow/', unfollow_user, name='unfollow_user'),  # Comentado
    path('users/<int:user_id>/toggle_follow/', toggle_follow_user, name='toggle_follow_user'),
    path('users/<int:user_id>/is_following/', get_follow_status, name='get_follow_status'),
    
    # Posts
    path('posts/', PostList.as_view(), name='post_list'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('posts/feed/', FeedList.as_view(), name='post_feed'),
    path('posts/<int:post_id>/like/', like_post, name='like_post'),
    
    # Comments
    path('posts/<int:post_id>/comments/', CommentListCreateAPIView.as_view(), name='comment_list_create'),
]