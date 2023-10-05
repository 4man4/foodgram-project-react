from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

# from .views import CustomUserViewSet

router = DefaultRouter()
# router.register('users', CustomUserViewSet)

urlpatterns = [
    path('auth/token/login/', views.obtain_auth_token),
    # re_path(r'^auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    # path('auth/', include('djoser.urls.authtoken')),
    # path('', include(router.urls)),
]
