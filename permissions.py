from rest_framework.permissions import BasePermission,SAFE_METHODS

class IsNotAuth(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated



class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser

class IsNotSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and not request.user.is_superuser


class IsOwnerOrReadOnly(BasePermission):
    message = 'You dont have access to this content!'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user