from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access based on user role"""
    allowed_roles = []  # ['photographer', 'client', 'assistant']
    
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        
        if user.is_staff:
            return True
        
        for role in self.allowed_roles:
            if hasattr(user, f'{role}profile'):
                return True
        
        return False
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('accounts:login')


class PhotographerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict to photographers only"""
    
    def test_func(self):
        user = self.request.user
        return user.is_staff or hasattr(user, 'photographerprofile')


class ClientRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict to clients only"""
    
    def test_func(self):
        user = self.request.user
        return hasattr(user, 'clientprofile')


class AssistantRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict to assistant photographers only"""
    
    def test_func(self):
        user = self.request.user
        return hasattr(user, 'assistantprofile')
