"""
Authentication and Account Management Services
Clean, reusable business logic for user operations
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db import transaction
from django.conf import settings

from apps.accounts.models import CustomUser, PhotographerProfile, ClientProfile, AssistantProfile, UserRole


class AuthenticationService:
    """Handle user authentication operations"""
    
    @staticmethod
    def register_user(username, email, password, role, **extra_fields):
        """
        Register a new user with role
        
        Args:
            username: Unique username
            email: Email address
            password: Plain text password
            role: User role (photographer, client, assistant)
            **extra_fields: Additional fields (first_name, last_name, etc.)
        
        Returns:
            tuple: (user, error_message)
        """
        try:
            with transaction.atomic():
                # Check if user exists
                if CustomUser.objects.filter(email=email).exists():
                    return None, "Email already registered"
                
                if CustomUser.objects.filter(username=username).exists():
                    return None, "Username already taken"
                
                # Create user
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    **extra_fields
                )
                
                # Create role-specific profile
                if role == UserRole.PHOTOGRAPHER:
                    PhotographerProfile.objects.create(user=user)
                elif role == UserRole.CLIENT:
                    ClientProfile.objects.create(user=user)
                elif role == UserRole.ASSISTANT:
                    AssistantProfile.objects.create(user=user)
                
                return user, None
                
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def login_user(request, username, password):
        """
        Authenticate and login user
        
        Returns:
            tuple: (user, error_message)
        """
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            return None, "Invalid credentials"
        
        if not user.is_active_account:
            return None, "Account is deactivated"
        
        login(request, user)
        return user, None
    
    @staticmethod
    def logout_user(request):
        """Logout current user"""
        logout(request)
    
    @staticmethod
    def send_password_reset_email(user):
        """Send password reset email"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        context = {
            'user': user,
            'uid': uid,
            'token': token,
        }
        
        subject = 'Password Reset Request'
        message = render_to_string('accounts/emails/password_reset.html', context)
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    
    @staticmethod
    def reset_password(uid, token, new_password):
        """Reset user password with token"""
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return True, None
            else:
                return False, "Invalid token"
        except CustomUser.DoesNotExist:
            return False, "User not found"
        except Exception as e:
            return False, str(e)


class ProfileService:
    """Handle user profile operations"""
    
    @staticmethod
    def get_photographer_profile(user):
        """Get photographer profile or create if not exists"""
        if not user.is_photographer:
            return None
        
        profile, created = PhotographerProfile.objects.get_or_create(user=user)
        return profile
    
    @staticmethod
    def update_photographer_profile(user, **kwargs):
        """Update photographer profile"""
        if not user.is_photographer:
            return False, "Not a photographer"
        
        profile = PhotographerProfile.objects.get(user=user)
        
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.save()
        return True, None
    
    @staticmethod
    def get_client_profile(user):
        """Get client profile"""
        if not user.is_client:
            return None
        
        profile, created = ClientProfile.objects.get_or_create(user=user)
        return profile
    
    @staticmethod
    def update_user_profile(user, **kwargs):
        """Update base user profile"""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.save()
        return True, None
    
    @staticmethod
    def get_available_photographers(city=None, specialty=None):
        """Get list of available photographers with filters"""
        queryset = CustomUser.objects.filter(
            role=UserRole.PHOTOGRAPHER,
            is_active_account=True,
            photographer_profile__is_available=True
        )
        
        if city:
            queryset = queryset.filter(city=city)
        
        if specialty:
            queryset = queryset.filter(
                photographer_profile__specialties__icontains=specialty
            )
        
        return queryset.select_related('photographer_profile')