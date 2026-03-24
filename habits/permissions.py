from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Разрешение, позволяющее редактировать только владельца объекта."""

    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return obj.user == request.user


class IsOwner(BasePermission):
    """Разрешение, позволяющее доступ только владельцу объекта."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
