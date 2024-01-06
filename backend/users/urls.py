from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, SubscriptionsViewSet

router = DefaultRouter()
router.register('subscriptions', SubscriptionsViewSet, basename='subscriptions')
router.register('subscribe', SubscriptionsViewSet, basename='subscribe')
# router.register('set_password', include('djoser.urls.set_password'))
# router.register('', UserViewSet)

urlpatterns = [
    path(r'', include('djoser.urls')),
    # re_path(r'^users/', include('djoser.urls')),
    re_path(r'^users/', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
