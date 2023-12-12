from pprint import pprint

from django.db.models import Sum, OuterRef, Exists, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from rest_framework import viewsets, status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from .serializers import (
    TagSerializer,
    IngredientSerializer,
    CreateRecipeSerializer,
    ShowRecipeSerializer,
    # SpecialRecipeSerializer,
    FavoriteShopCartSerializer,
    # ShoppingCartSerializer,
)
from users.serializers import SpecialRecipeSerializer
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


class TagView(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permissions = (AllowAny,)
    pagination_class = None


class IngredientsView(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = IngredientFilter
    search_fields = ('name',)
    pagination_class = None


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permissions = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return CreateRecipeSerializer
        return ShowRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        return Recipe.objects.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    recipe=OuterRef('pk'),
                    user=self.request.user
                )
            ),
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    recipe=OuterRef('pk'),
                    user=self.request.user
                )
            )
        )


# class FavoriteView(APIView):
#     permissions = (IsAuthenticatedOrReadOnly,)
#
#     def post(self, request, pk):
#         user = request.user
#         data = {'user': user.pk, 'recipe': pk}
#         serializer = FavoriteSerializer(
#             data=data,
#             context={'request': request}
#         )
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         user = request.user
#         recipe = get_object_or_404(Recipe, pk=pk)
#         serializer = FavoriteSerializer(
#             data={'user': user.pk, 'recipe': pk},
#             context={'request': request}
#         )
#         if serializer.is_valid(raise_exception=True):
#             queryset = Favorite.objects.filter(user=user, recipe=recipe)
#             queryset.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteShopCartView(APIView):
    permissions = (IsAuthenticatedOrReadOnly,)

    # def post(self, request, pk):
    #     user = request.user
    #     recipe = get_object_or_404(Recipe, pk=pk)
    #     # if Favorite.objects.filter(user=user, recipe=recipe).exists():
    #     #     return Response(
    #     #         {"detail": "Рецепт уже добавлен в избранное"},
    #     #         status=status.HTTP_400_BAD_REQUEST
    #     #     )
    #     data = {
    #         'id': recipe.id,
    #         'name': recipe.name,
    #         'image': recipe.image,
    #         'cooking_time': recipe.cooking_time,
    #     }
    #     context = {
    #         'request': request,
    #         'recipe': recipe,
    #     }
    #     serializer = FavoriteSerializer(instance=recipe, context=context)
    #     if serializer.is_valid(raise_exception=True):
    #         Favorite.objects.create(user=user, recipe=recipe)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def post(self, request, pk):
    #     recipe = get_object_or_404(Recipe, pk=pk)
    #     context = {
    #         'request': request,
    #         'recipe': recipe,
    #     }
    #     serializer = FavoriteSerializer(data=recipe, context=context)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, pk):
        # user = request.user
        # recipe = get_object_or_404(Recipe, pk=pk)
        # fav_instance = Favorite(user=user, recipe=recipe)
        # pprint(request.path)
        serializer = FavoriteShopCartSerializer(
            data={'user': request.user.pk, 'recipe': pk},
            context={'request': request},
        )
        if serializer.is_valid(raise_exception=True):
            # fav_instance.save()
            serializer.save()
            # fav_serializer = FavoriteSerializer(fav_instance)
            # return Response(fav_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def delete(self, request, pk):
    #     user = request.user
    #     recipe = get_object_or_404(Recipe, pk=pk)
    #     data = {
    #         'id': recipe.id,
    #         'name': recipe.name,
    #         'image': recipe.image,
    #         'cooking_time': recipe.cooking_time,
    #     }
    #     context = {
    #         'request': request,
    #         'recipe': recipe,
    #     }
    #     # if not Favorite.objects.filter(user=user, recipe=recipe).exists():
    #     #     return Response(
    #     #         {"detail": "Рецепта нет в избранном"},
    #     #         status=status.HTTP_400_BAD_REQUEST
    #     #     )
    #     serializer = FavoriteSerializer(instance=recipe, context=context)
    #     if serializer.is_valid(raise_exception=True):
    #         Favorite.objects.filter(user=user, recipe=recipe).delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)

    # def delete(self, request, pk):
    #     recipe = get_object_or_404(Recipe, pk=pk)
    #     context = {
    #         'request': request,
    #         'recipe': recipe,
    #     }
    #     serializer = FavoriteSerializer(data=recipe, context=context)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.delete()
    #         return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    # Рабочая версия !!!!!!!!!!!!!!!!!!!!!!
    # def delete(self, request, pk):
    #     user = request.user
    #     recipe = get_object_or_404(Recipe, pk=pk)
    #     try:
    #         favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
    #     except Http404:
    #         raise ValidationError({'errors': ['Рецепта нет в избранном.']})
    #     favorite.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model = Favorite if 'favorite' in request.path else ShoppingCart
        serializer = FavoriteShopCartSerializer(
            data={'user': user.pk, 'recipe': pk},
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            queryset = model.objects.filter(user=user, recipe=recipe)
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        # err_msg = exc.detail['errors'][0]
        # pprint(err_msg)
        if isinstance(exc, ValidationError):
            return Response(
                {'errors': exc.detail['errors'][0]},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)


# class ShoppingCartView(APIView):
#     permission_classes = (IsAuthenticated,)
#     # pagination_class = None
#
#     def post(self, request, pk):
#         # user = request.user
#         # data = {'user': user.pk, 'recipe': pk}
#         serializer = ShoppingCartSerializer(
#             data={'user': request.user.pk, 'recipe': pk},
#             context={'request': request}
#         )
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         user = request.user
#         recipe = get_object_or_404(Recipe, id=pk)
#         serializer = ShoppingCartSerializer(
#             data={'user': user.pk, 'recipe': pk},
#             context={'request': request}
#         )
#         if serializer.is_valid(raise_exception=True):
#             queryset = ShoppingCart.objects.filter(user=user, recipe=recipe)
#             queryset.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
