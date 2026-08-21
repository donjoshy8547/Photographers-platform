from django import forms
from .models import Photo, Tag, PhotoTag, DownloadRequest


class PhotoUploadForm(forms.ModelForm):
    """Form for uploading photos"""
    event = forms.ModelChoiceField(
        queryset=None,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Photo
        fields = ['image', 'event', 'title', 'description']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'multiple': True,
                'accept': 'image/*'
            }),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Show only events the user has access to
            from apps.events.models import Event
            if user.is_staff:
                self.fields['event'].queryset = Event.objects.all()
            elif hasattr(user, 'photographerprofile'):
                self.fields['event'].queryset = Event.objects.filter(
                    photographer=user.photographerprofile
                )
            else:
                self.fields['event'].queryset = Event.objects.none()


class PhotoEditForm(forms.ModelForm):
    """Form for editing photo metadata"""
    class Meta:
        model = Photo
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class TagForm(forms.ModelForm):
    """Form for creating tags"""
    class Meta:
        model = Tag
        fields = ['name', 'tag_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tag_type': forms.Select(attrs={'class': 'form-control'}),
        }


class DownloadRequestForm(forms.ModelForm):
    """Form for requesting photo downloads"""
    class Meta:
        model = DownloadRequest
        fields = ['download_type', 'photo', 'gallery', 'event', 'selected_photos']
        widgets = {
            'download_type': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.Select(attrs={'class': 'form-control'}),
            'gallery': forms.Select(attrs={'class': 'form-control'}),
            'event': forms.Select(attrs={'class': 'form-control'}),
            'selected_photos': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limit choices based on user permissions
        if user and hasattr(user, 'clientprofile'):
            # Clients can only download from their events
            from apps.events.models import Event, Gallery
            self.fields['event'].queryset = Event.objects.filter(
                client=user.clientprofile
            )
            self.fields['gallery'].queryset = Gallery.objects.filter(
                event__client=user.clientprofile
            )
