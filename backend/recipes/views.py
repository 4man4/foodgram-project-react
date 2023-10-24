from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView

from . import serializers
from .filters import IngredientFilter, RecipeFilter
from .models import (
    Recipe,
    Ingredient,
    RecipeIngredients,
    Tag,
    # RecipeTags,
    Favorite,
    ShoppingCart,
)


class TagView(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permissions = (AllowAny,)
    pagination_class = None


class IngredientsView(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = serializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter
    search_fields = ('name',)
    pagination_class = None


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permissions = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        method = self.request.method
        if method == 'POST' or method == 'PATCH':
            return serializers.CreateRecipeSerializer
        return serializers.ShowRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class FavoriteView(APIView):
    permissions = (IsAuthenticatedOrReadOnly,)

    @action(
        methods=[
            'post',
        ],
        detail=True,
    )
    def post(self, request, pk):
        user = request.user
        data = {
            'user': user.id,
            'recipe': pk,
        }
        if Favorite.objects.filter(
            user=user, recipe__id=pk
        ).exists():
            return Response(
                {'Ошибка': 'Уже в избранном'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = serializers.FavoriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE', ], detail=True,)
    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not Favorite.objects.filter(
            user=user, recipe=recipe
        ).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(APIView):

    permission_classes = (IsAuthenticated,)
    pagination_class = None

    @action(methods=['post'], detail=True,)
    def post(self, request, pk):
        user = request.user
        data = {'user': user.id, 'recipe': pk}
        serializer = serializers.ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(
                {'errors': 'Ошибка запроса'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if ShoppingCart.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': 'Этот рецепт уже добавлен в корзину'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(method=['delete'], detail=True)
    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredients = RecipeIngredients.objects.filter(
        recipe__shoppingcart__user=request.user
    ).order_by('ingredient__name').values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))
    shopping_list = 'Список покупок:'
    for ingredient in ingredients:
        shopping_list += (
            f'\n{ingredient["ingredient__name"]} - '
            f'{ingredient["amount"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
        )
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=shopping_list.txt'
    return response
