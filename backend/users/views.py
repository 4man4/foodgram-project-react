from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.validators import custom_exception
from .serializers import (
    UserSerializer,
    CreateUserSerializer,
    PasswordSerializer,
    SubscriptionsSerializer,
)

from .models import User, Follow


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return CreateUserSerializer

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if 'password' in self.request.data:
            password = make_password(self.request.data['password'])
            serializer.save(password=password)
        else:
            serializer.save()

    def perform_update(self, serializer):
        if 'password' in self.request.data:
            password = make_password(self.request.data['password'])
            serializer.save(password=password)
        else:
            serializer.save()

    @action(
        ['post'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request, *args, **kwargs):
        user = self.request.user
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        serializer = SubscriptionsSerializer(
            author,
            data=request.data,
            context={'request': request, 'user': user, 'author': author},
        )
        if (request.method == 'POST'
                and serializer.is_valid(raise_exception=True)):
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif (request.method == 'DELETE'
              and serializer.is_valid(raise_exception=True)):
            queryset = Follow.objects.filter(user=user, author=author)
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def handle_exception(self, exc):
        return custom_exception(exc)


class SubscriptionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
