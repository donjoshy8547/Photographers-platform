"""
Admin Configuration for Accounts App
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import CustomUser, PhotographerProfile, ClientProfile, AssistantProfile


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Custom user admin with role-based fields"""
    
    list_display = ('username', 'email', 'role', 'city', 'is_active_account', 'created_at')
    list_filter = ('role', 'is_active_account', 'email_verified', 'city')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Role & Status'), {'fields': ('role', 'is_active_account', 'email_verified')}),
        (_('Location'), {'fields': ('city', 'country')}),
        (_('Contact'), {'fields': ('phone_number', 'bio')}),
        (_('Profile'), {'fields': ('profile_picture',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PhotographerProfile)
class PhotographerProfileAdmin(admin.ModelAdmin):
    """Admin for photographer profiles"""
    
    list_display = ('user', 'specialties', 'hourly_rate', 'is_available', 'average_rating')
    list_filter = ('is_available', 'city')
    search_fields = ('user__username', 'specialties', 'equipment_list')
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Professional Info'), {
            'fields': ('specialties', 'years_experience', 'equipment_list')
        }),
        (_('Portfolio'), {
            'fields': ('portfolio_url', 'instagram_url')
        }),
        (_('Pricing'), {
            'fields': ('hourly_rate', 'package_prices')
        }),
        (_('Availability'), {
            'fields': ('is_available', 'max_events_per_month')
        }),
        (_('Ratings'), {
            'fields': ('average_rating', 'total_reviews')
        }),
    )


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    """Admin for client profiles"""
    
    list_display = ('user', 'event_preferences', 'min_budget', 'max_budget')
    search_fields = ('user__username', 'event_preferences')
    filter_horizontal = ('preferred_photographers',)


@admin.register(AssistantProfile)
class AssistantProfileAdmin(admin.ModelAdmin):
    """Admin for assistant profiles"""
    
    list_display = ('user', 'supervising_photographer', 'skills', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('user__username', 'skills', 'certifications')