from rest_framework import permissions


class IsOwnerAdminOrStaffReadOnly(permissions.BasePermission):
    """
    Object-level access for Habit and HabitLog (both expose an `owner`).

    - Admins: full access.
    - Staff: read anything, but only modify their own objects.
    - Users: owners only.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_admin:
            return True
        if user.is_privileged and request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == user
