from rest_framework import permissions


# permissions for users DELETE endpoint
class UserPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action in ['destroy']:
            return request.user.is_authenticated and obj == request.user

        return True