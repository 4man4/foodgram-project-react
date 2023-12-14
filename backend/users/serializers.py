from rest_framework import serializers

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
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=obj,
        ).exists()


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


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


class SubscriptionsSerializer(UserSerializer):
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
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return SpecialRecipeSerializer(
            recipes,
            many=True,
            read_only=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, data):
        request = self.context.get('request')
        user = self.context.get('user')
        author = self.context.get('author')
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
            and not Follow.objects.filter(user=user, author=author).exists()
        ):
            raise serializers.ValidationError({'errors': 'Вы не подписаны.'})
        return data
