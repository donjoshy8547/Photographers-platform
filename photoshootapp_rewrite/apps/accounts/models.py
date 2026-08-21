"""
User Models - Custom user model with role-based access
Supports: Admin, Photographer, Client, Assistant Photographer
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """User role choices"""
    ADMIN = 'admin', _('Admin')
    PHOTOGRAPHER = 'photographer', _('Photographer')
    CLIENT = 'client', _('Client')
    ASSISTANT = 'assistant', _('Assistant Photographer')


class CustomUser(AbstractUser):
    """
    Custom User Model with role-based access control
    Extends Django's AbstractUser for additional fields
    """
    
    # Role field (required)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
        verbose_name=_('User Role')
    )
    
    # Profile fields
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Phone Number')
    )
    
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name=_('Profile Picture')
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=1000,
        verbose_name=_('Bio')
    )
    
    # Location
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('City')
    )
    
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Country')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    # Email verification
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('Email Verified')
    )
    
    # Account status
    is_active_account = models.BooleanField(
        default=True,
        verbose_name=_('Account Active')
    )
    
    class Meta:
        db_table = 'auth_users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active_account']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def is_photographer(self):
        """Check if user is photographer"""
        return self.role == UserRole.PHOTOGRAPHER
    
    @property
    def is_client(self):
        """Check if user is client"""
        return self.role == UserRole.CLIENT
    
    @property
    def is_assistant(self):
        """Check if user is assistant"""
        return self.role == UserRole.ASSISTANT
    
    @property
    def is_admin_user(self):
        """Check if user is admin"""
        return self.role == UserRole.ADMIN or self.is_superuser


class PhotographerProfile(models.Model):
    """
    Extended profile for photographers
    Contains portfolio, pricing, and availability info
    """
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='photographer_profile',
        limit_choices_to={'role': UserRole.PHOTOGRAPHER},
        verbose_name=_('User')
    )
    
    # Professional info
    specialties = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=_('Comma-separated list of photography specialties'),
        verbose_name=_('Specialties')
    )
    
    years_experience = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Years of Experience')
    )
    
    equipment_list = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Equipment List')
    )
    
    # Portfolio
    portfolio_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Portfolio URL')
    )
    
    instagram_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Instagram URL')
    )
    
    # Pricing
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Hourly Rate')
    )
    
    package_prices = models.JSONField(
        blank=True,
        null=True,
        help_text=_('JSON structure for package pricing'),
        verbose_name=_('Package Prices')
    )
    
    # Availability
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Available for Bookings')
    )
    
    max_events_per_month = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Max Events Per Month')
    )
    
    # Ratings
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Average Rating')
    )
    
    total_reviews = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Reviews')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'photographer_profiles'
        verbose_name = _('Photographer Profile')
        verbose_name_plural = _('Photographer Profiles')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class ClientProfile(models.Model):
    """
    Extended profile for clients
    Contains preferences and booking history
    """
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='client_profile',
        limit_choices_to={'role': UserRole.CLIENT},
        verbose_name=_('User')
    )
    
    # Preferences
    preferred_photographers = models.ManyToManyField(
        CustomUser,
        related_name='preferred_by_clients',
        blank=True,
        limit_choices_to={'role': UserRole.PHOTOGRAPHER},
        verbose_name=_('Preferred Photographers')
    )
    
    event_preferences = models.TextField(
        blank=True,
        null=True,
        help_text=_('Types of events client typically books'),
        verbose_name=_('Event Preferences')
    )
    
    # Budget range
    min_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Minimum Budget')
    )
    
    max_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Maximum Budget')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'client_profiles'
        verbose_name = _('Client Profile')
        verbose_name_plural = _('Client Profiles')
    
    def __str__(self):
        return f"{self.user.username}'s Client Profile"


class AssistantProfile(models.Model):
    """
    Profile for assistant photographers
    Links to supervising photographer
    """
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='assistant_profile',
        limit_choices_to={'role': UserRole.ASSISTANT},
        verbose_name=_('User')
    )
    
    # Supervision
    supervising_photographer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assistants',
        limit_choices_to={'role': UserRole.PHOTOGRAPHER},
        verbose_name=_('Supervising Photographer')
    )
    
    # Skills
    skills = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=_('Comma-separated list of skills'),
        verbose_name=_('Skills')
    )
    
    certifications = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Certifications')
    )
    
    # Availability
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Available')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assistant_profiles'
        verbose_name = _('Assistant Profile')
        verbose_name_plural = _('Assistant Profiles')
    
    def __str__(self):
        return f"{self.user.username}'s Assistant Profile"