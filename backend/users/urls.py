from django.urls import path, re_path, include

from .views import SubscriptionsViewSet

urlpatterns = [
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
