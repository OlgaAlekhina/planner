from requests import request
from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """ разрешает пользователю просматривать, редактировать и удалять только свой собственный профиль """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action in ['destroy', 'retrieve', 'partial_update']:
            return request.user.is_authenticated and obj == request.user

        return True


class GroupPermission(permissions.BasePermission):
    """ разрешает пользователю удалять, редактировать и добавлять участников только в свою собственную группу """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action in ['destroy', 'add_user', 'partial_update', 'groups_actions']:
            return request.user.is_authenticated and obj.owner == request.user

        # проверяем, что текущий пользователь состоит в группе, для выдачи доступа к просмотру участников группы
        if view.action in ['retrieve']:
            return request.user.is_authenticated and any(i in obj.group_users.all() for i in request.user.users.all())

        return True




