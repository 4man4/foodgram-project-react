from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, SubscriptionsViewSet

router = DefaultRouter()
router.register('subscriptions', SubscriptionsViewSet, basename='subscriptions')
router.register('', UserViewSet)

urlpatterns = [
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('users/', include(router.urls)),
]
