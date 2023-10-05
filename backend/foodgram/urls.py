from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/docs/', TemplateView.as_view(template_name='docs/redoc.html')),
    path('api/', include('users.urls')),
    # path('api/', include('recipes.urls')),
    # path('api/', include('api.urls')),
    # path("api/docs/", TemplateView.as_view(template_name='docs')),
]
