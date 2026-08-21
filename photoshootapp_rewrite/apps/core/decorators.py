from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def role_required(allowed_roles=[]):
    """Decorator to restrict views based on user role"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            
            if user.is_staff:
                return view_func(request, *args, **kwargs)
            
            for role in allowed_roles:
                if hasattr(user, f'{role}profile'):
                    return view_func(request, *args, **kwargs)
            
            return HttpResponseForbidden("You don't have permission to access this page.")
        
        return _wrapped_view
    return decorator


def photographer_required(view_func):
    """Decorator to restrict to photographers"""
    return role_required(['photographer'])(view_func)


def client_required(view_func):
    """Decorator to restrict to clients"""
    return role_required(['client'])(view_func)


def assistant_required(view_func):
    """Decorator to restrict to assistants"""
    return role_required(['assistant'])(view_func)
