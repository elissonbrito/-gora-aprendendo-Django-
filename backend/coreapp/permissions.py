from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return getattr(request, 'user_obj', None) and request.user_obj.role == 'ADMIN'

class IsAdminOrCollaboratorRole(BasePermission):
    def has_permission(self, request, view):
        return getattr(request, 'user_obj', None) and request.user_obj.role in ['ADMIN', 'COLLABORATOR']
