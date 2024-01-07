import re

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from recipes.models import Recipe
from .models import User, Follow


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField('get_is_subscribed')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and request.user.follower.filter(author=obj).exists())


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = '__all__'


class SpecialRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowSubscriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.SerializerMethodField('get_recipes_count')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if bool(re.match(r'^\d+$', recipes_limit)):
            recipes = recipes[:int(recipes_limit)]
        return SpecialRecipeSerializer(
            recipes,
            many=True,
            read_only=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class EditSubscriptionsSerializer(ShowSubscriptionsSerializer):
    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        author = get_object_or_404(User, id=self.context['request'].parser_context['kwargs']['pk'])
        # author = self.context.get('author')
        if (
                request.method == 'POST'
                and Follow.objects.filter(user=user, author=author).exists()
        ):
            raise serializers.ValidationError({'errors': 'Вы уже подписаны.'})
        if (
                request.method == 'POST'
                and user.pk == author.pk
        ):
            raise serializers.ValidationError(
                {'errors': 'Невозможно подписаться на себя.'}
            )
        if (
                request.method == 'DELETE'
                and not Follow.objects.filter(
                    user=user,
                    author=author
                ).exists()
        ):
            raise serializers.ValidationError({'errors': 'Вы не подписаны.'})
        return author
