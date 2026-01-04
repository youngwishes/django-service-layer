from rest_framework import permissions


class CustomerRequired(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(getattr(request.user, "customer", None))
