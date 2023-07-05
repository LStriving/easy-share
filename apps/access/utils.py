from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # check if the user is the owner or an admin
        print(f"Staff:{request.user.is_staff}")
        return request.user == obj.user or request.user.is_staff