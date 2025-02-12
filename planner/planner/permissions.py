from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """ разрешает пользователю просматривать и удалять только свой собственный профиль """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action in ['destroy', 'retrieve']:
            return request.user.is_authenticated and obj == request.user

        return True


class GroupPermission(permissions.BasePermission):
    """ разрешает пользователю удалять, редактировать и добавлять участников только в свою собственную группу """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action in ['destroy', 'add_user', 'partial_update']:
            return request.user.is_authenticated and obj.owner == request.user

        return True