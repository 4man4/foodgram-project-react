from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router_v1 = DefaultRouter()



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('users.urls')),
    path('api/', include('recipes.urls')),
]
