from rest_framework import permissions

class IsSurveyorOrHigher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['SURVEYOR', 'SUPERVISOR', 'ADMIN']