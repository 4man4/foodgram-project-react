from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from .serializers import (
    ShowSubscriptionsSerializer,
    EditSubscriptionsSerializer,
)
from .models import User, Follow


class SubscriptionsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if self.request.method == 'GET':
            return User.objects.filter(following__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'DELETE']:
            return EditSubscriptionsSerializer
        return ShowSubscriptionsSerializer

    def do_validation(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, pk=kwargs['pk'])
        serializer = self.get_serializer(data={
            'user': user,
            'author': author,
        })
        serializer.is_valid(raise_exception=True)
        return {'user': user, 'author': author, 'serializer': serializer}

    def create(self, request, *args, **kwargs):
        validated = self.do_validation(request, **kwargs)
        Follow.objects.create(
            user=validated['user'],
            author=validated['author'],
        )
        return Response(validated['serializer'].data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        validated = self.do_validation(request, **kwargs)
        self.perform_destroy(
            Follow.objects.filter(
                user=validated['user'],
                author=validated['author'],
            )
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
