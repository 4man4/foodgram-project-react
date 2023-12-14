from django.contrib.admin.decorators import register
from django.contrib.admin.options import ModelAdmin, TabularInline
from django.contrib.admin.sites import site

from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     RecipeTags, ShoppingCart, Tag)


class RecipeIngredientsInline(TabularInline):
    model = RecipeIngredients
    extra = 1


class RecipeTagsInline(TabularInline):
    model = RecipeTags
    extra = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    inlines = (
        RecipeIngredientsInline,
        RecipeTagsInline,
    )
    list_display = (
        'id',
        'name',
        'author',
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
    )


@register(Tag)
class TagAdmin(ModelAdmin):
    pass


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'user'
    )


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    pass


site.empty_value_display = 'Не задано'
