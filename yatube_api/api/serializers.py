from rest_framework import serializers
from django.contrib.auth import get_user_model
from posts.models import Post, Comment, Follow
from posts.models import Group

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    group = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Group.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model = Post
        fields = ('id', 'text', 'pub_date', 'author', 'image', 'group')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'text', 'created')
        read_only_fields = ('post',)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate_following(self, value):
        request = self.context.get('request')
        if request and request.user == value:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        following = validated_data['following']

        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError(
                {'following': 'Вы уже подписаны на этого пользователя'}
            )

        return Follow.objects.create(
            user=user,
            following=following
        )
