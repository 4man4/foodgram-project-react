from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, SubscriptionsViewSet

# router = DefaultRouter()
# router.register('users/subscriptions/', SubscriptionsViewSet, basename='subscriptions')
# router.register('users/subscribe/', SubscriptionsViewSet, basename='subscribe')
# router.register('', include('djoser.urls'))
# router.register('', UserViewSet)

urlpatterns = [
    # re_path(r'^users/', include('djoser.urls')),
    # re_path(r'^users/', include(router.urls)),
    # path(r'', include(router.urls)),
    path('users/subscriptions/', SubscriptionsViewSet.as_view({
        'get': 'list',
    }),),
    path('users/<int:pk>/subscribe/', SubscriptionsViewSet.as_view({
        'post': 'create',
        'delete': 'destroy',
    }),),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
