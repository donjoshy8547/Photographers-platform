from django.db import models
from django.conf import settings
from apps.events.models import Event, Gallery
import uuid
import os


class Photo(models.Model):
    """Model for storing photos with metadata"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='photos')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', blank=True, null=True)
    
    # Metadata
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Technical metadata
    file_size = models.BigIntegerField(default=0)  # in bytes
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    format = models.CharField(max_length=10, blank=True)  # JPEG, PNG, etc.
    
    # AI tags
    is_processed = models.BooleanField(default=False)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['-uploaded_at']),
            models.Index(fields=['event', '-uploaded_at']),
            models.Index(fields=['is_processed']),
        ]
    
    def __str__(self):
        return f"Photo {self.id} - {self.event.name if self.event else 'No Event'}"
    
    def get_filename(self):
        return os.path.basename(self.image.name)
    
    def get_file_extension(self):
        return os.path.splitext(self.image.name)[1].lower()


class Tag(models.Model):
    """Model for photo tags (AI-generated or manual)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    tag_type = models.CharField(
        max_length=20,
        choices=[
            ('ai_face', 'AI Face'),
            ('ai_object', 'AI Object'),
            ('ai_scene', 'AI Scene'),
            ('manual', 'Manual'),
            ('emotion', 'Emotion'),
        ],
        default='manual'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.tag_type})"


class PhotoTag(models.Model):
    """Through model for many-to-many relationship between photos and tags"""
    
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='photo_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='photo_tags')
    confidence = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)  # AI confidence score
    bounding_box = models.JSONField(null=True, blank=True)  # For face/object detection boxes
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['photo', 'tag']
        indexes = [
            models.Index(fields=['photo', 'tag']),
        ]
    
    def __str__(self):
        return f"{self.photo.id} - {self.tag.name}"


class FaceRecognition(models.Model):
    """Store face recognition data for photos"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='face_recognitions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recognized_faces')
    
    bounding_box = models.JSONField()  # {x, y, width, height}
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    recognized_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recognized_at']
        indexes = [
            models.Index(fields=['user', '-recognized_at']),
        ]
    
    def __str__(self):
        return f"Face in {self.photo.id} - {self.user.username}"


class DownloadRequest(models.Model):
    """Track photo download requests and bulk exports"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='download_requests')
    
    # Download type
    download_type = models.CharField(
        max_length=20,
        choices=[
            ('single', 'Single Photo'),
            ('gallery', 'Gallery'),
            ('event', 'Event'),
            ('selected', 'Selected Photos'),
        ]
    )
    
    # Related objects
    photo = models.ForeignKey(Photo, on_delete=models.SET_NULL, null=True, blank=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    
    # For selected photos
    selected_photos = models.JSONField(default=list, blank=True)  # List of photo UUIDs
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('ready', 'Ready'),
            ('failed', 'Failed'),
            ('expired', 'Expired'),
        ],
        default='pending'
    )
    
    download_url = models.URLField(blank=True, null=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    downloaded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Download {self.id} by {self.user.username}"
