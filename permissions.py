from rest_framework.permissions import BasePermission

class IsNotAuth(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated



class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser

class IsNotSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and not request.user.is_superuser