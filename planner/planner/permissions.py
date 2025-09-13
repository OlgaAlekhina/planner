from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """
    разрешает пользователю просматривать, редактировать и удалять только свой собственный профиль
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action in ['destroy', 'retrieve', 'partial_update']:
            return request.user.is_authenticated and obj == request.user

        return True


class GroupPermission(permissions.BasePermission):
    """
    разрешает пользователю удалять, редактировать, добавлять и просматривать участников только в своей собственной группе
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action in ['destroy', 'add_user', 'partial_update', 'groups_actions']:
            return request.user.is_authenticated and obj.owner == request.user

        # проверяем, что текущий пользователь состоит в группе, для выдачи доступа к просмотру участников группы
        if view.action in ['retrieve']:
            return request.user.is_authenticated and any(i in obj.users.all() for i in request.user.group_users.all())

        return True


class EventPermission(permissions.BasePermission):
    """
    разрешает пользователю удалять и редактировать только созданные им события и просматривать только те события, в
    которых он является автором или участником
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action in ['destroy', 'partial_update']:
            return request.user.is_authenticated and obj.author == request.user

        # проверяем, что текущий пользователь является автором или участником события, для выдачи доступа к просмотру
        # этого события
        if view.action in ['retrieve']:
            return request.user.is_authenticated and (obj.author == request.user or request.user in [groupuser.user for
                                                                                         groupuser in obj.users.all()])
        return True


class NotePermission(permissions.BasePermission):
    """
    разрешает пользователю работать только со своими собственными заметками
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        return obj.author == request.user


class TaskPermission(permissions.BasePermission):
    """
    разрешает пользователю работать только со своими собственными задачами
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        return obj.author == request.user







