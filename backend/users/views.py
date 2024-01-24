from rest_framework import status, views
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


class SubscriptionsViewSet(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        subscriptions = User.objects.filter(following__user=self.request.user)
        paginator = CustomPagination()
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
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        serializer = EditSubscriptionsSerializer(
            data={'user': user.pk, 'author': pk},
            context={'request': request},
        )
        if serializer.is_valid(raise_exception=True):
            queryset = Follow.objects.filter(user=user, author=pk)
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
