from django.db.models import Sum, OuterRef, Exists, Value
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView

from .serializers import (
    TagSerializer,
    IngredientSerializer,
    CreateRecipeSerializer,
    ShowRecipeSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)
from .filters import IngredientFilter, RecipeFilter
from .models import (
    Recipe,
    Ingredient,
    RecipeIngredients,
    Tag,
    Favorite,
    ShoppingCart,
)
from foodgram.permissions import IsAuthorOrAdminOrReadOnly, IsAdminOrReadOnly


class TagView(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientsView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('name',)
    pagination_class = None


class RecipeView(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return CreateRecipeSerializer
        return ShowRecipeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Recipe.objects.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        recipe=OuterRef('pk'),
                        user=user
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        recipe=OuterRef('pk'),
                        user=user
                    )
                )
            )
        return Recipe.objects.annotate(
            is_favorited=Value(False),
            is_in_shopping_cart=Value(False)
        )


class UsingRecipesView(APIView):
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    serializer_class = None
    model = None

    def post(self, request, pk):
        serializer = self.serializer_class(
            data={'user': request.user.pk, 'recipe': pk},
            context={'request': request},
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = self.serializer_class(
            data={'user': user.pk, 'recipe': pk},
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            queryset = self.model.objects.filter(user=user, recipe=recipe)
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteView(UsingRecipesView):
    serializer_class = FavoriteSerializer
    model = Favorite


class ShoppingCartView(UsingRecipesView):
    serializer_class = ShoppingCartSerializer
    model = ShoppingCart


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
