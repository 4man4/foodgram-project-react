from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, mixins, views, generics
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from .serializers import (
    ShowSubscriptionsSerializer,
    EditSubscriptionsSerializer,
)
from .models import User, Follow
from foodgram.pagination import CustomPagination


# class SubscriptionList(generics.CreateAPIView):
#     # queryset = Follow.objects.all()
#     serializer_class = EditSubscriptionsSerializer
#
#     def get_queryset(self):
#         author_id = self.kwargs.get('author_id', None)
#         if author_id is not None:
#             return Follow.objects.filter(author_id=author_id)
#         return Follow.objects.none()
#
class SubscriptionsViewSet(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        subscriptions = User.objects.filter(following__user=self.request.user)
        paginator = CustomPagination()
        # paginator.page_size = request.query_params.get('limit', 10)
        paginated_queryset = paginator.paginate_queryset(subscriptions, request)
        serializer = ShowSubscriptionsSerializer(
            paginated_queryset,
            context={'request': request},
            many=True,
        )
        return paginator.get_paginated_response(data=serializer.data)

    def post(self, request, pk):
        serializer = EditSubscriptionsSerializer(
            data={'user': request.user.pk, 'author': pk},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        # if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        # author = get_object_or_404(User, pk=pk)
        serializer = EditSubscriptionsSerializer(
            data={'user': user.pk, 'author': pk},
            context={'request': request},
        )
        if serializer.is_valid(raise_exception=True):
            queryset = Follow.objects.filter(user=user, author=pk)
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CreateListDestroyViewSet(
#     viewsets.GenericViewSet,
#     mixins.CreateModelMixin,
#     mixins.ListModelMixin,
#     mixins.DestroyModelMixin
# ):
#     pass
#
#
# class SubscriptionsViewSet(CreateListDestroyViewSet):
#     permission_classes = (IsAuthenticated,)
#
#     def get_serializer_class(self):
#         if self.request.method in ['POST', 'DELETE']:
#             return EditSubscriptionsSerializer
#         return ShowSubscriptionsSerializer
#
#     def get_queryset(self):
#         # if self.request.method == 'GET':
#             # return Follow.objects.all()
#             # return Follow.objects.filter(user=self.request.user)
#             # return User.objects.filter(following__user=self.request.user)
#         return self.request.user.follower.all()
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class SubscriptionsViewSet(viewsets.ModelViewSet):
#     permission_classes = (IsAuthenticated,)
#
#     def get_serializer_class(self):
#         if self.request.method in ['POST', 'DELETE']:
#             return EditSubscriptionsSerializer
#         return ShowSubscriptionsSerializer
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context.update({'request': self.request})
#         return context
#
#     def get_queryset(self):
#         if self.request.method == 'GET':
#             return Follow.objects.filter(user=self.request.user)
#             # return User.objects.filter(following__user=self.request.user)
#
#     def do_validation(self, request, **kwargs):
#         user = request.user
#         author = get_object_or_404(User, pk=kwargs['pk'])
#         serializer = self.get_serializer(data={
#             'user': user.pk,
#             'author': author.pk,
#         })
#         serializer.is_valid(raise_exception=True)
#         return {'user': user, 'author': author, 'serializer': serializer}
#
#     def create(self, request, *args, **kwargs):
#         validated = self.do_validation(request, **kwargs)
#         # Follow.objects.create(
#         #     user=validated['user'],
#         #     author=validated['author'],
#         # )
#         return Response(validated['serializer'].data, status=status.HTTP_201_CREATED)
#
#     def destroy(self, request, *args, **kwargs):
#         validated = self.do_validation(request, **kwargs)
#         self.perform_destroy(
#             Follow.objects.filter(
#                 user=validated['user'],
#                 author=validated['author'],
#             )
#         )
#         return Response(status=status.HTTP_204_NO_CONTENT)
