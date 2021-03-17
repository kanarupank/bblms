from django.core.serializers.json import Serializer
from rest_framework import serializers
from .models import User, UserStats, Game, Team, Player, Coach, PlayerStats, TeamStats


class FlattenMixin(object):
    """Flatens the specified related objects in this representation"""

    def to_representation(self, obj):
        assert hasattr(self.Meta, 'flatten'), (
            'Class {serializer_class} missing "Meta.flatten" attribute'.format(
                serializer_class=self.__class__.__name__
            )
        )
        # Get the current object representation
        rep = super(FlattenMixin, self).to_representation(obj)
        # Iterate the specified related objects with their serializer
        for field, serializer_class in self.Meta.flatten:
            serializer = serializer_class(context=self.context)
            objrep = serializer.to_representation(getattr(obj, field))
            # Include their fields, prefixed, in the current   representation
            for key in objrep:
                rep[key] = objrep[key]
        return rep


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role']


class TeamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('user_id', 'team_id', 'height')


class PlayerUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Player
        fields = ('user', 'team_id')


class TeamPlayerSerializer(FlattenMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ('id',)
        flatten = [('user', TeamUserSerializer)]


# class TeamPlayerSerializer(serializers.ModelSerializer):
#     user = TeamUserSerializer(many=False, read_only=True)
#
#     class Meta:
#         model = Player
#         fields = ('user',)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'team_name')


class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ('user_id', 'team_id')


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('team_one', 'team_two', 'team_one_score',
                  'team_two_score', 'winner', 'date', 'round')


class TopPlayerSerializer(serializers.Serializer):
    # def get_dump_object(self, obj):
    #     mapped_object = {
    #         'first_name': obj.first_name,
    #         'last_name': obj.last_name,
    #         'average_score': obj.average_score
    #     }
    first_name = serializers.CharField(max_length=500)
    last_name = serializers.CharField(max_length=500)
    average_score = serializers.DecimalField(max_digits=4, decimal_places=2)
