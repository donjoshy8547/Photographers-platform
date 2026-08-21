"""
Events App Models
Event management, bookings, and applications
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class EventType(models.TextChoices):
    """Event type choices"""
    WEDDING = 'wedding', _('Wedding')
    PORTRAIT = 'portrait', _('Portrait')
    EVENT = 'event', _('Event')
    COMMERCIAL = 'commercial', _('Commercial')
    FASHION = 'fashion', _('Fashion')
    OTHER = 'other', _('Other')


class EventStatus(models.TextChoices):
    """Event status choices"""
    DRAFT = 'draft', _('Draft')
    PENDING = 'pending', _('Pending Approval')
    APPROVED = 'approved', _('Approved')
    IN_PROGRESS = 'in_progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')
    CANCELLED = 'cancelled', _('Cancelled')


class BookingStatus(models.TextChoices):
    """Booking status choices"""
    PENDING = 'pending', _('Pending')
    CONFIRMED = 'confirmed', _('Confirmed')
    COMPLETED = 'completed', _('Completed')
    CANCELLED = 'cancelled', _('Cancelled')


class Event(models.Model):
    """
    Event model - represents a photoshoot event
    """
    
    # Basic info
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.OTHER,
        verbose_name=_('Event Type')
    )
    
    # Date & Time
    date = models.DateField(verbose_name=_('Event Date'))
    start_time = models.TimeField(blank=True, null=True, verbose_name=_('Start Time'))
    end_time = models.TimeField(blank=True, null=True, verbose_name=_('End Time'))
    duration_hours = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Duration (hours)')
    )
    
    # Location
    location = models.CharField(max_length=500, verbose_name=_('Location'))
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('City'))
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Country'))
    
    # Relationships
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events_hosted',
        limit_choices_to={'role__in': ['client', 'admin']},
        verbose_name=_('Host')
    )
    
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events_photographed',
        limit_choices_to={'role': 'photographer'},
        verbose_name=_('Photographer')
    )
    
    assistants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='events_assisting',
        blank=True,
        limit_choices_to={'role': 'assistant'},
        verbose_name=_('Assistants')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT,
        verbose_name=_('Status')
    )
    
    # Budget
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Budget')
    )
    
    # Additional info
    special_requests = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Special Requests')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'events'
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['status']),
            models.Index(fields=['event_type']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.date})"


class Booking(models.Model):
    """
    Booking model - client booking request for photographer
    """
    
    # Relationships
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='booking',
        verbose_name=_('Event')
    )
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        limit_choices_to={'role': 'client'},
        verbose_name=_('Client')
    )
    
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='photographer_bookings',
        limit_choices_to={'role': 'photographer'},
        verbose_name=_('Photographer')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name=_('Status')
    )
    
    # Message
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Message to Photographer')
    )
    
    # Pricing
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('Total Price')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking: {self.event.title} - {self.photographer.username}"


class EventApplication(models.Model):
    """
    Event Application - photographers apply to host's event
    """
    
    # Relationships
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name=_('Event')
    )
    
    photographer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_applications',
        limit_choices_to={'role': 'photographer'},
        verbose_name=_('Photographer')
    )
    
    # Application details
    cover_letter = models.TextField(
        verbose_name=_('Cover Letter')
    )
    
    proposed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Proposed Price')
    )
    
    portfolio_samples = models.JSONField(
        blank=True,
        null=True,
        help_text=_('IDs of sample photos to showcase'),
        verbose_name=_('Portfolio Samples')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('withdrawn', 'Withdrawn'),
        ],
        default='pending',
        verbose_name=_('Status')
    )
    
    # Host response
    host_response = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Host Response')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_applications'
        verbose_name = _('Event Application')
        verbose_name_plural = _('Event Applications')
        unique_together = [['event', 'photographer']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.photographer.username} applied for {self.event.title}"