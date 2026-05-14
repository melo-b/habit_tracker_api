from rest_framework import permissions

class IsOwnerAdminOrStaffReadOnly(permissions.BasePermission):
    """
    Custom permission for Habit and HabitLog object-level access.
    """
    def has_object_permission(self, request, view, obj):
        # Admins have full access to everything
        if request.user.role == 'admin':
            return True
            
        # Staff can view everything (SAFE_METHODS are GET, HEAD, OPTIONS)
        # but can only edit their own objects
        if request.user.role == 'staff':
            if request.method in permissions.SAFE_METHODS:
                return True
                
        # Determine the owner of the object (Habit has 'user', HabitLog has 'habit.user')
        owner = obj.user if hasattr(obj, 'user') else obj.habit.user
        
        # Standard users (and Staff trying to edit) must be the owner
        return owner == request.user