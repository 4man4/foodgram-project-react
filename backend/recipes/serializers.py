from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

import foodgram.constants as const
from users.models import User
from users.serializers import UserSerializer
from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < const.MIN_VALUE_INGREDIENT_AMOUNT:
            raise serializers.ValidationError(
                'Укажите корректное количество ингредиента',
                status.HTTP_400_BAD_REQUEST,
            )
        return value


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class CreateUpdateRecipeSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    def validate_cooking_time(self, value):
        if value < const.MIN_COOKING_TIME:
            raise serializers.ValidationError(
                ('Введите число большее '
                    f'или равное {const.MIN_COOKING_TIME}'),
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
        for tag in value:
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
        for ingredient in value:
            ingredient_id = ingredient['id'].id
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    f'Ингредиент "{ingredient_id}" повторяется',
                    status.HTTP_400_BAD_REQUEST,
                )
            ingredients_list.append(ingredient_id)
        return value

    def make_ingredients(self, recipe, ingredients):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(
                RecipeIngredients(
                    recipe=recipe,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount'],
                )
            )
        RecipeIngredients.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data,
        )
        recipe.is_favorited = False
        recipe.is_in_shopping_cart = False
        recipe.tags.set(tags)
        self.make_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        self.make_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ShowRecipeSerializer(
            instance,
            context={'request': self.context.get('request')},
        ).data


class ShowRecipeSerializer(RecipeSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source='recipeingredients',
        many=True,
    )
    image = Base64ImageField(max_length=None, use_url=True)
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + (
            'is_favorited',
            'is_in_shopping_cart',
        )


class UsingRecipesSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
    )
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = ('user', 'recipe')
        model = None

    error_message_already_exists = ''
    error_message_not_exists = ''

    def validate(self, data):
        request = self.context.get('request')
        is_recipe_added = self.Meta.model.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists()
        if request.method == 'POST' and is_recipe_added:
            raise serializers.ValidationError(
                {'errors': self.error_message_already_exists}
            )
        if request.method == 'DELETE' and not is_recipe_added:
            raise serializers.ValidationError(
                {'errors': self.error_message_not_exists}
            )
        return data

    def create(self, validated_data):
        return self.Meta.model.objects.create(**validated_data)

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')},
        ).data


class FavoriteSerializer(UsingRecipesSerializer):
    class Meta(UsingRecipesSerializer.Meta):
        model = Favorite

    error_message_already_exists = 'Рецепт уже добавлен в избранное.'
    error_message_not_exists = 'Рецепта нет в избранном.'


class ShoppingCartSerializer(UsingRecipesSerializer):
    class Meta(UsingRecipesSerializer.Meta):
        model = ShoppingCart

    error_message_already_exists = 'Рецепт уже добавлен в корзину покупок.'
    error_message_not_exists = 'Рецепта нет в корзине покупок.'
