from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Like, Comment

User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    user_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'user_profile_picture', 'text', 'created_at')

    def get_user_profile_picture(self, obj):
        if obj.user.profile_picture:
            return obj.user.profile_picture.url
        return None

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    author_profile_picture = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 'author', 'author_profile_picture', 'caption', 'image',
            'likes_count', 'comments_count', 'is_liked', 'comments', 'created_at'
        )

    def get_author_profile_picture(self, obj):
        if obj.author.profile_picture:
            return obj.author.profile_picture.url
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('caption', 'image')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        post = Post.objects.create(**validated_data)
        
        # Update user's posts count
        post.author.posts_count += 1
        post.author.save()
        
        return post
