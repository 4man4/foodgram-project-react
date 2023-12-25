from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

import foodgram.constants as const
from users.models import User
from users.serializers import UserSerializer, SpecialRecipeSerializer
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    RecipeTags,
    ShoppingCart,
    Tag,
)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id',)
    name = serializers.ReadOnlyField(source='ingredient.name',)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source='recipeingredients',
        many=True,
    )
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()
    image = Base64ImageField(max_length=None, use_url=True)
    # image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class CreateRecipeSerializer(ShowRecipeSerializer):
    # image = Base64ImageField(max_length=None, use_url=True)
    # author = UserSerializer(read_only=True)
    # ingredients = AddRecipeIngredientsSerializer(many=True)
    # cooking_time = serializers.IntegerField()
    # tags = serializers.PrimaryKeyRelatedField(
    #     queryset=Tag.objects.all(),
    #     many=True,
    # )
    #
    # class Meta:
    #     model = Recipe
    #     fields = (
    #         'id',
    #         'tags',
    #         'author',
    #         'ingredients',
    #         'name',
    #         'image',
    #         'text',
    #         'cooking_time',
    #     )

    def validate_cooking_time(self, value):
        if value <= const.MIN_COOKING_TIME:
            raise serializers.ValidationError(
                'Введите число больше 0',
                status.HTTP_400_BAD_REQUEST,
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо выбрать теги',
                status.HTTP_400_BAD_REQUEST,
            )
        tags_list = []
        all_tags = self.context['all_tags']
        # all_tags = Tag.objects.all().values_list('id', flat=True)
        for tag in value:
            if not (tag.pk in all_tags):
                raise serializers.ValidationError(
                    f'Тег {tag} не существует',
                    status.HTTP_404_NOT_FOUND,
                )
            if tag.pk in tags_list:
                raise serializers.ValidationError(
                    f'Тег {tag} повторяется',
                    status.HTTP_400_BAD_REQUEST,
                )
            tags_list.append(tag.pk)
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо выбрать ингредиенты',
                status.HTTP_400_BAD_REQUEST,
            )
        ingredients_list = []
        all_ingredients = self.context['all_ingredients']
        # all_ingredients = Ingredient.objects.all().values_list('id', flat=True)
        for ingredient in value:
            ingredient_instance = ingredient['id']
            if not (ingredient_instance.pk in all_ingredients):
                raise serializers.ValidationError(
                    f'Ингредиент "{ingredient_instance.name}" не существует',
                    status.HTTP_404_NOT_FOUND,
                )
            if ingredient_instance.pk in ingredients_list:
                raise serializers.ValidationError(
                    f'Ингредиент "{ingredient_instance.name}" повторяется',
                    status.HTTP_400_BAD_REQUEST,
                )
            ingredients_list.append(ingredient_instance.pk)
            if ingredient['amount'] < const.MIN_INGREDIENT_AMOUNT:
                raise serializers.ValidationError(
                    'Укажите корректное количество '
                    f'ингредиента "{ingredient_instance.name}"',
                    status.HTTP_400_BAD_REQUEST,
                )
        return value

    def make_ingredients(self, recipe, ingredients, tags):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(
                RecipeIngredients(
                    recipe=recipe,
                    # ingredient=Ingredient.objects.get(
                    #     id=ingredient['id'].pk
                    # ),
                    ingredient=ingredient['id'].pk,
                    amount=ingredient['amount'],
                )
            )
        RecipeIngredients.objects.bulk_create(ingredient_list)
        recipe.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        self.make_ingredients(recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        RecipeTags.objects.filter(recipe=instance).delete()
        RecipeIngredients.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.make_ingredients(instance, ingredients, tags)
        return super().update(instance, validated_data)

    # def to_representation(self, instance):
    #     return ShowRecipeSerializer(
    #         instance,
    #         context={'request': self.context.get('request')}
    #     ).data


# class ShowRecipeSerializer(RecipeSerializer):
    # tags = TagSerializer(read_only=True, many=True)
    # author = UserSerializer(read_only=True)
    # ingredients = RecipeIngredientsSerializer(
    #     source='recipeingredients',
    #     many=True,
    # )
    # is_favorited = serializers.BooleanField()
    # is_in_shopping_cart = serializers.BooleanField()
    # image = Base64ImageField()
    #
    # class Meta:
    #     model = Recipe
    #     fields = (
    #         'id',
    #         'tags',
    #         'author',
    #         'ingredients',
    #         'is_favorited',
    #         'is_in_shopping_cart',
    #         'name',
    #         'image',
    #         'text',
    #         'cooking_time',
    #     )
    # pass


class FavoriteShopCartSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
    )
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    def get_model(self, url):
        if 'favorite' in url:
            return Favorite
        elif 'shopping_cart' in url:
            return ShoppingCart

    def validate(self, data):
        request = self.context.get('request')
        queryset = (self.get_model(request.path).objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists())
        if (
            request.method == 'POST'
            and queryset
        ):
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже добавлен.'}
            )
        if (
            request.method == 'DELETE'
            and not queryset
        ):
            raise serializers.ValidationError(
                {'errors': 'Рецепт не добавлен.'}
            )
        return data

    def create(self, validated_data):
        return (self.get_model(self.context.get('request').path)
                .objects.create(**validated_data))

    def to_representation(self, instance):
        recipe = SpecialRecipeSerializer(instance.recipe)
        return recipe.data
