from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Post, Like, Comment
from .serializers import PostSerializer, PostCreateSerializer, CommentSerializer

User = get_user_model()

class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get posts from followed users + own posts
        following_users = self.request.user.following.values_list('following', flat=True)
        return Post.objects.filter(
            author__in=list(following_users) + [self.request.user.id]
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer

class PostDetailView(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            # Update user's posts count
            instance.author.posts_count -= 1
            instance.author.save()
            instance.delete()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post
    )
    
    if created:
        post.likes_count += 1
        post.save()
        return Response({'message': 'Post liked'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Already liked'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unlike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    try:
        like = Like.objects.get(user=request.user, post=post)
        like.delete()
        post.likes_count -= 1
        post.save()
        return Response({'message': 'Post unliked'}, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        return Response({'error': 'Not liked yet'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    text = request.data.get('text', '').strip()
    
    if not text:
        return Response({'error': 'Comment text is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    comment = Comment.objects.create(
        user=request.user,
        post=post,
        text=text
    )
    
    post.comments_count += 1
    post.save()
    
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        user = get_object_or_404(User, username=username)
        return Post.objects.filter(author=user)
