"""
URL configuration for planner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework import routers
from users.views import UserViewSet, GroupViewSet, add_missing_profiles


schema_view = get_schema_view(
    openapi.Info(
        title="Planner API",
        # description="Planner API",
        default_version='v1',),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('planner/admin/', admin.site.urls),
    path('planner/', RedirectView.as_view(pattern_name='schema-swagger-ui', permanent=True)),
    path('planner/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('planner/api-auth/', include('rest_framework.urls')),
    path('planner/api/', include(router.urls)),
    path('planner/add_missing_profiles/', add_missing_profiles, name='add_missing_profiles'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
