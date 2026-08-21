from django.urls import path
from . import views

app_name = 'media_library'

urlpatterns = [
    # Photo views
    path('', views.PhotoListView.as_view(), name='photo_list'),
    path('upload/', views.PhotoUploadView.as_view(), name='photo_upload'),
    path('upload/event/<uuid:event_id>/', views.PhotoUploadView.as_view(), name='photo_upload_event'),
    path('<uuid:pk>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('<uuid:pk>/edit/', views.PhotoEditView.as_view(), name='photo_edit'),
    path('<uuid:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo_delete'),
    path('<uuid:photo_id>/process/', views.api_process_photo, name='photo_process'),
    
    # Tag views
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/create/', views.TagCreateView.as_view(), name='tag_create'),
    path('photos/<uuid:photo_id>/tags/add/', views.AddTagToPhotoView.as_view(), name='tag_add'),
    path('photos/<uuid:photo_id>/tags/<uuid:tag_id>/remove/', views.RemoveTagFromPhotoView.as_view(), name='tag_remove'),
    
    # Download views
    path('downloads/create/', views.DownloadRequestView.as_view(), name='download_create'),
    path('downloads/<uuid:pk>/', views.DownloadRequestDetailView.as_view(), name='download_detail'),
    
    # Personal views
    path('my-photos/', views.MyPhotosView.as_view(), name='my_photos'),
    
    # API endpoints
    path('api/search/', views.api_search_photos, name='api_search_photos'),
]
