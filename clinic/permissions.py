from rest_framework.permissions import BasePermission

from clinic.models import User


class IsAdminRole(BasePermission):
    """Full access for admin-role users."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsClinicianOrAdmin(BasePermission):
    """Clinicians can view/update patients and diseases; admins have full access."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == User.Role.ADMIN:
            return True
        if request.user.role == User.Role.CLINICIAN:
            return request.method in ('GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH')
        return False


class IsReceptionOrAbove(BasePermission):
    """Reception staff can register patients and view doctor schedules."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in (
            User.Role.ADMIN,
            User.Role.CLINICIAN,
            User.Role.RECEPTION,
        )

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True
        if request.user.role == User.Role.CLINICIAN:
            return request.method in ('GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH')
        if request.user.role == User.Role.RECEPTION:
            return request.method in ('GET', 'HEAD', 'OPTIONS', 'POST')
        return False
