from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from django.db.models import Value

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
    id = serializers.IntegerField(source='ingredient.id',)
    name = serializers.ReadOnlyField(source='ingredient.name',)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        if not value:
            raise serializers.ValidationError(
                'Укажите корректное количество '
                f'ингредиента "{value}"',
                status.HTTP_400_BAD_REQUEST,
            )
        return value


# class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
#         queryset=Ingredient.objects.all()
#     )
#
#     class Meta:
#         model = RecipeIngredients
#         fields = ('id', 'amount')
#
#
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(read_only=True, many=True)
    # author = UserSerializer(read_only=True)
    # ingredients = RecipeIngredientsSerializer(
    #     source='recipeingredients',
    #     many=True,
    # )

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


class CreateRecipeSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True)
    # ingredients = AddIngredientToRecipeSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    # cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    # class Meta(RecipeSerializer.Meta):
    #     pass
        # fields = RecipeSerializer.Meta.fields
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

    def get_is_favorited(self):
        # user = self.context.get('request').user
        # return Favorite.objects.filter(user=user, recipe=instance).exists()
        return False

    def get_is_in_shopping_cart(self):
        return False

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
        # all_tags = self.context['all_tags']
        # all_tags = Tag.objects.all().values_list('id', flat=True)
        for tag in value:
            # if not (tag.pk in all_tags):
            #     raise serializers.ValidationError(
            #         f'Тег {tag} не существует',
            #         status.HTTP_404_NOT_FOUND,
            #     )
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
        # all_ingredients = self.context['all_ingredients']
        # all_ingredients = Ingredient.objects.all().values_list('id', flat=True)
        for ingredient in value:
            ingredient_id = ingredient['ingredient']['id']
            # if not (ingredient_id in all_ingredients):
            #     raise serializers.ValidationError(
            #         f'Ингредиент "{ingredient_id}" не существует',
            #         status.HTTP_404_NOT_FOUND,
            #     )
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    f'Ингредиент "{ingredient_id}" повторяется',
                    status.HTTP_400_BAD_REQUEST,
                )
            ingredients_list.append(ingredient_id)
        return value

    def make_tags_ingredients(self, recipe, ingredients_obj, ingredients, tags):
        # amounts_val = []
        # for ingredient in ingredients:
        #     amounts_val.append(ingredient['amount'])
        # RecipeIngredients.objects.bulk_create(
        #     RecipeIngredients(
        #         recipe=recipe,
        #         ingredient__in=self.context['ingredients_obj'],
        #         amount__in=amounts_val,
        #     )
        # )

        ingredient_list = []
        for counter in range(len(ingredients)):
            ingredient_list.append(
                RecipeIngredients(
                    recipe=recipe,
                    ingredient=ingredients_obj[counter],
                    # ingredient=ingredient['ingredient']['id'],
                    # ingredient=ingredient['id'].pk,
                    amount=ingredients[counter]['amount'],
                )
            )
        RecipeIngredients.objects.bulk_create(ingredient_list)
        recipe.tags.set(tags)

    def create(self, validated_data):
        ingredients_obj = self.context['ingredients_obj']
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data,
        )
        recipe.is_favorited = False
        recipe.is_in_shopping_cart = False
        self.make_tags_ingredients(recipe, ingredients_obj, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        RecipeTags.objects.filter(recipe=instance).delete()
        RecipeIngredients.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.make_tags_ingredients(instance, ingredients, tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ShowRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class ShowRecipeSerializer(RecipeSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source='recipeingredients',
        many=True,
    )
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()
    image = Base64ImageField(max_length=None, use_url=True)
    cooking_time = serializers.IntegerField()


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
