# backend/apps/users/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Follow
from .serializers import UserSerializer

User = get_user_model()

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if user_to_follow == request.user:
        return Response({'error': 'You cannot follow yourself'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if created:
        # Update counts
        request.user.following_count += 1
        request.user.save()
        user_to_follow.followers_count += 1
        user_to_follow.save()
        
        return Response({'message': 'Successfully followed'}, 
                       status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Already following'}, 
                       status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    
    try:
        follow = Follow.objects.get(
            follower=request.user,
            following=user_to_unfollow
        )
        follow.delete()
        
        # Update counts
        request.user.following_count -= 1
        request.user.save()
        user_to_unfollow.followers_count -= 1
        user_to_unfollow.save()
        
        return Response({'message': 'Successfully unfollowed'}, 
                       status=status.HTTP_200_OK)
    except Follow.DoesNotExist:
        return Response({'error': 'Not following this user'}, 
                       status=status.HTTP_400_BAD_REQUEST)

