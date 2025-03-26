# booksblog/permissions.py
from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешает доступ только владельцу объекта или администратору.
    Для безопасных методов (GET, HEAD, OPTIONS) доступ разрешён всем.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (чтение) всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Для изменения/удаления проверяем, является ли пользователь владельцем или админом
        # Проверяем поле, которое указывает на владельца (author или user)
        owner = getattr(obj, 'author', getattr(obj, 'user', None))
        return owner == request.user or request.user.is_staff

class IsAdminOnly(permissions.BasePermission):
    """
    Разрешает доступ только администраторам.
    Для безопасных методов (GET, HEAD, OPTIONS) доступ разрешён всем.
    """
    def has_permission(self, request, view):
        # Разрешаем безопасные методы (чтение) всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Для изменения/удаления разрешаем только админам
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (чтение) всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Для изменения/удаления разрешаем только админам
        return request.user and request.user.is_staff