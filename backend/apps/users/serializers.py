from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

User = get_user_model()

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ('id', 'username', 'email', 'password')

class UserSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()
    is_followed_by = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'bio', 'profile_picture',
            'is_private', 'followers_count', 'following_count',
            'posts_count', 'website', 'is_following', 'is_followed_by'
        )
        read_only_fields = ('followers_count', 'following_count', 'posts_count')

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(follower=request.user).exists()
        return False

    def get_is_followed_by(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.following.filter(following=request.user).exists()
        return False
