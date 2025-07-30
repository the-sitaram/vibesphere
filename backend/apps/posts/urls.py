from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/', views.like_post, name='like-post'),
    path('posts/<int:post_id>/unlike/', views.unlike_post, name='unlike-post'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add-comment'),
    path('users/<str:username>/posts/', views.UserPostsView.as_view(), name='user-posts'),
]
