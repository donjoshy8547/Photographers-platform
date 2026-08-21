from django.contrib import admin
from .models import Photo, Tag, PhotoTag, FaceRecognition, DownloadRequest


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['get_filename', 'event', 'gallery', 'is_processed', 'processing_status', 'uploaded_at']
    list_filter = ['is_processed', 'processing_status', 'uploaded_at', 'event']
    search_fields = ['title', 'description', 'event__name']
    readonly_fields = ['id', 'file_size', 'width', 'height', 'format', 'uploaded_at', 'updated_at']
    
    fieldsets = (
        ('Image', {
            'fields': ('image', 'thumbnail', 'event', 'gallery')
        }),
        ('Metadata', {
            'fields': ('title', 'description')
        }),
        ('Technical Info', {
            'fields': ('file_size', 'width', 'height', 'format'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('is_processed', 'processing_status'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'tag_type', 'created_at']
    list_filter = ['tag_type', 'created_at']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at']


@admin.register(PhotoTag)
class PhotoTagAdmin(admin.ModelAdmin):
    list_display = ['photo', 'tag', 'confidence', 'created_at']
    list_filter = ['tag__tag_type', 'created_at']
    search_fields = ['photo__title', 'tag__name']
    readonly_fields = ['created_at']
    raw_id_fields = ['photo', 'tag']


@admin.register(FaceRecognition)
class FaceRecognitionAdmin(admin.ModelAdmin):
    list_display = ['photo', 'user', 'confidence', 'recognized_at']
    list_filter = ['recognized_at', 'user']
    search_fields = ['photo__title', 'user__username']
    readonly_fields = ['id', 'bounding_box', 'recognized_at']
    raw_id_fields = ['photo', 'user']


@admin.register(DownloadRequest)
class DownloadRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'download_type', 'status', 'created_at', 'downloaded_at']
    list_filter = ['download_type', 'status', 'created_at']
    search_fields = ['user__username', 'id']
    readonly_fields = ['id', 'selected_photos', 'download_url', 'expires_at', 'created_at', 'downloaded_at']
    raw_id_fields = ['user', 'photo', 'gallery', 'event']
