from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings

from .models import Photo, Tag, PhotoTag, DownloadRequest, FaceRecognition
from apps.events.models import Event, Gallery
from .forms import PhotoUploadForm, PhotoEditForm, TagForm, DownloadRequestForm


class PhotoListView(LoginRequiredMixin, ListView):
    """List all photos with filtering options"""
    model = Photo
    template_name = 'media_library/photo_list.html'
    context_object_name = 'photos'
    paginate_by = 24
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by event
        event_id = self.request.GET.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        # Filter by gallery
        gallery_id = self.request.GET.get('gallery')
        if gallery_id:
            queryset = queryset.filter(gallery_id=gallery_id)
        
        # Filter by tag
        tag_id = self.request.GET.get('tag')
        if tag_id:
            queryset = queryset.filter(photo_tags__tag_id=tag_id)
        
        # Search by title/description
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) | 
                models.Q(description__icontains=search)
            )
        
        # Filter by processing status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(processing_status=status)
        
        return queryset.select_related('event', 'gallery').prefetch_related('photo_tags__tag')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.all()
        context['tags'] = Tag.objects.all()
        context['current_event'] = self.request.GET.get('event')
        context['current_tag'] = self.request.GET.get('tag')
        return context


class PhotoDetailView(LoginRequiredMixin, DetailView):
    """Display photo details with tags and metadata"""
    model = Photo
    template_name = 'media_library/photo_detail.html'
    context_object_name = 'photo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = self.object
        
        # Get related photos from same event
        context['related_photos'] = Photo.objects.filter(
            event=photo.event
        ).exclude(id=photo.id)[:8]
        
        # Get all available tags for adding
        context['available_tags'] = Tag.objects.exclude(
            id__in=photo.photo_tags.values_list('tag_id', flat=True)
        )
        
        return context


class PhotoUploadView(LoginRequiredMixin, CreateView):
    """Upload new photos"""
    model = Photo
    form_class = PhotoUploadForm
    template_name = 'media_library/photo_upload.html'
    success_url = reverse_lazy('media_library:photo_list')
    
    def form_valid(self, form):
        # Set event from URL or form
        event_id = self.kwargs.get('event_id') or form.cleaned_data.get('event')
        form.instance.event_id = event_id
        
        # Set uploader (photographer or assistant)
        form.instance.uploaded_by = self.request.user
        
        messages.success(self.request, 'Photo(s) uploaded successfully!')
        return super().form_valid(form)


class PhotoEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit photo metadata"""
    model = Photo
    form_class = PhotoEditForm
    template_name = 'media_library/photo_edit.html'
    success_url = reverse_lazy('media_library:photo_list')
    
    def test_func(self):
        photo = self.get_object()
        user = self.request.user
        return (
            user.is_staff or
            user == photo.event.photographer or
            (hasattr(user, 'assistantprofile') and user.assistantprofile.photographer == photo.event.photographer)
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to edit this photo.')
        return redirect('media_library:photo_list')


class PhotoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a photo"""
    model = Photo
    template_name = 'media_library/photo_confirm_delete.html'
    success_url = reverse_lazy('media_library:photo_list')
    
    def test_func(self):
        photo = self.get_object()
        user = self.request.user
        return user.is_staff or user == photo.event.photographer
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Photo deleted successfully.')
        return super().delete(request, *args, **kwargs)


class TagListView(LoginRequiredMixin, ListView):
    """List all tags"""
    model = Tag
    template_name = 'media_library/tag_list.html'
    context_object_name = 'tags'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        tag_type = self.request.GET.get('type')
        if tag_type:
            queryset = queryset.filter(tag_type=tag_type)
        return queryset


class TagCreateView(LoginRequiredMixin, CreateView):
    """Create a new tag"""
    model = Tag
    form_class = TagForm
    template_name = 'media_library/tag_form.html'
    success_url = reverse_lazy('media_library:tag_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Tag "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class AddTagToPhotoView(LoginRequiredMixin, CreateView):
    """Add a tag to a photo"""
    model = PhotoTag
    template_name = 'media_library/add_tag.html'
    
    def post(self, request, *args, **kwargs):
        photo_id = kwargs.get('photo_id')
        tag_id = request.POST.get('tag_id')
        
        photo = get_object_or_404(Photo, id=photo_id)
        tag = get_object_or_404(Tag, id=tag_id)
        
        # Check if tag already exists
        if PhotoTag.objects.filter(photo=photo, tag=tag).exists():
            messages.warning(request, 'Tag already added to this photo.')
        else:
            PhotoTag.objects.create(photo=photo, tag=tag, confidence=1.0)
            messages.success(request, f'Tag "{tag.name}" added to photo.')
        
        return redirect('media_library:photo_detail', pk=photo_id)


class RemoveTagFromPhotoView(LoginRequiredMixin, DeleteView):
    """Remove a tag from a photo"""
    model = PhotoTag
    success_url = reverse_lazy('media_library:photo_list')
    
    def delete(self, request, *args, **kwargs):
        phototag = self.get_object()
        photo_id = phototag.photo.id
        messages.success(request, f'Tag removed from photo.')
        self.object.delete()
        return redirect('media_library:photo_detail', pk=photo_id)


class DownloadRequestView(LoginRequiredMixin, CreateView):
    """Create a download request for photos"""
    model = DownloadRequest
    form_class = DownloadRequestForm
    template_name = 'media_library/download_request.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Set expiration (7 days from now)
        from datetime import timedelta
        from django.utils import timezone
        form.instance.expires_at = timezone.now() + timedelta(days=7)
        
        messages.success(self.request, 'Download request created. You will be notified when ready.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('media_library:download_detail', kwargs={'pk': self.object.id})


class DownloadRequestDetailView(LoginRequiredMixin, DetailView):
    """View download request status"""
    model = DownloadRequest
    template_name = 'media_library/download_detail.html'
    context_object_name = 'download_request'
    
    def get_queryset(self):
        return DownloadRequest.objects.filter(user=self.request.user)


class MyPhotosView(LoginRequiredMixin, ListView):
    """Show photos where the current user is tagged/recognized"""
    model = Photo
    template_name = 'media_library/my_photos.html'
    context_object_name = 'photos'
    paginate_by = 24
    
    def get_queryset(self):
        user = self.request.user
        # Get photos where user is recognized via face recognition
        recognized_photo_ids = FaceRecognition.objects.filter(
            user=user
        ).values_list('photo_id', flat=True)
        
        return Photo.objects.filter(
            models.Q(id__in=recognized_photo_ids) |
            models.Q(photo_tags__tag__name__icontains=user.username)
        ).distinct().select_related('event')


# API Views for AJAX operations
def api_process_photo(request, photo_id):
    """Trigger AI processing for a photo"""
    if request.method == 'POST':
        photo = get_object_or_404(Photo, id=photo_id)
        
        # Check permissions
        if not (request.user.is_staff or request.user == photo.event.photographer):
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Trigger async processing
        from apps.ai_engine.tasks import process_photo_task
        process_photo_task.delay(str(photo.id))
        
        return JsonResponse({'status': 'processing', 'message': 'AI processing started'})
    
    return JsonResponse({'error': 'Invalid method'}, status=405)


def api_search_photos(request):
    """API endpoint for searching photos"""
    query = request.GET.get('q', '')
    event_id = request.GET.get('event')
    tag_name = request.GET.get('tag')
    
    queryset = Photo.objects.all()
    
    if query:
        queryset = queryset.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(photo_tags__tag__name__icontains=query)
        )
    
    if event_id:
        queryset = queryset.filter(event_id=event_id)
    
    if tag_name:
        queryset = queryset.filter(photo_tags__tag__name__icontains=tag_name)
    
    photos = queryset.select_related('event')[:20]  # Limit results
    
    results = [
        {
            'id': str(photo.id),
            'title': photo.title or photo.get_filename(),
            'thumbnail': photo.thumbnail.url if photo.thumbnail else photo.image.url,
            'event': photo.event.name if photo.event else None,
        }
        for photo in photos
    ]
    
    return JsonResponse({'results': results})
