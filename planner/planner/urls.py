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
from users.groups_views import GroupViewSet, add_default_group
from users.users_views import UserViewSet, add_missing_profiles
from events.views import EventViewSet, remove_users_from_event
from notes.views import NoteViewSet


# чтобы выводить 500 ошибку в формате JSON, а не HTML
handler500 = 'rest_framework.exceptions.server_error'

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
router.register(r'events', EventViewSet)
router.register(r'notes', NoteViewSet, basename='notes')

urlpatterns = [
    path('planner/admin/', admin.site.urls),
    path('planner/', RedirectView.as_view(pattern_name='schema-swagger-ui', permanent=True)),
    path('planner/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('planner/api-auth/', include('rest_framework.urls')),
    path('planner/api/', include(router.urls)),
    path('planner/add_missing_profiles/', add_missing_profiles, name='add_missing_profiles'),
    path('planner/add_default_group/', add_default_group, name='add_default_group'),
    path('planner/remove_users_from_event/', remove_users_from_event, name='remove_users_from_event'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
