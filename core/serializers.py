import core.models
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = core.models.User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_superuser', 'is_staff',
        )


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = core.models.Group
        fields = (
            'id', 'name',
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = core.models.Comment
        fields = (
            'id', 'content',
            'author', 'time_created', 'time_updated',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = core.models.Tag
        fields = (
            'id', 'name',
            'author', 'time_created', 'time_updated',
        )


class BoardStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = core.models.BoardState
        fields = (
            'id', 'rob_x', 'rob_y', 'data',
            'author', 'time_created', 'time_updated',
            'next_transitions', 'prev_transitions',
        )


class StateTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = core.models.StateTransition
        fields = (
            'id', 'source', 'target', 'label',
        )
