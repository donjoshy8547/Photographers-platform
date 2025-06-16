from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Events
import os
import base64
import traceback
import time

@csrf_exempt
def edit_image_view(request, event_id, image_id):
    """
    View function to display the image editor for a specific image.
    """
    pid = request.session.get('pid')
    if not pid:
        messages.error(request, "Please login to access this page")
        return redirect('/login')
    
    # Get the event details
    try:
        event = Events.objects.get(id=event_id, rid__pid=pid)
    except Events.DoesNotExist:
        messages.error(request, "Event not found or you don't have permission to access it")
        return redirect('/user-submit')
    
    # Get all images for this event
    images = []
    
    # Path to event-specific folder
    event_folder_name = f"event_{event_id}"
    export_dir = os.path.join(settings.MEDIA_ROOT, 'export_img', event_folder_name)
    
    # Path to photographer's selected_photos folder
    selected_photos_dir = os.path.join(settings.MEDIA_ROOT, 'selected_photos', f'pid_{pid}')
    
    # Get images from event-specific folder
    if os.path.exists(export_dir):
        for filename in os.listdir(export_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_path = os.path.join('export_img', event_folder_name, filename)
                images.append({
                    'name': filename,
                    'url': f'/media/{image_path}',
                    'path': os.path.join(export_dir, filename),
                    'source': 'event_folder'
                })
    
    # Get images from selected_photos folder
    if os.path.exists(selected_photos_dir):
        for filename in os.listdir(selected_photos_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Fix the path format with proper slashes
                image_rel_path = f'selected_photos/pid_{pid}/{filename}'
                # Check if this image is already in the list (to avoid duplicates)
                if not any(img['name'] == filename for img in images):
                    images.append({
                        'name': filename,
                        'url': f'/media/{image_rel_path}',
                        'path': os.path.join(selected_photos_dir, filename),
                        'source': 'selected_photos'
                    })
    
    # Check if the image_id is valid
    if image_id < 0 or image_id >= len(images):
        messages.error(request, "Invalid image selected")
        return redirect('user_submit_event', event_id=event_id)
    
    # Get the selected image
    selected_image = images[image_id]
    
    return render(request, "photograph/image_editor.html", {
        "event": event,
        "image_url": selected_image['url'],
        "image_name": selected_image['name'],
        "image_path": selected_image['path']
    })

@csrf_exempt
def save_edited_image(request):
    """
    View function to save an edited image.
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Only POST requests are accepted'
        })
    
    try:
        # Get the image data from the request
        image_data = request.POST.get('image_data')
        image_path = request.POST.get('image_path')
        event_id = request.POST.get('event_id')
        
        if not image_data or not image_path:
            return JsonResponse({
                'success': False,
                'message': 'Missing required parameters'
            })
        
        # Remove the data URL prefix
        if 'data:image/jpeg;base64,' in image_data:
            image_data = image_data.replace('data:image/jpeg;base64,', '')
        elif 'data:image/png;base64,' in image_data:
            image_data = image_data.replace('data:image/png;base64,', '')
        
        # Decode the base64 data
        image_bytes = base64.b64decode(image_data)
        
        # Clean up the image path to ensure it's valid
        # Replace any potential problematic characters
        image_path = image_path.replace('\x01', '')
        
        # Ensure the directory exists
        directory = os.path.dirname(image_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Save the image to the file system, overwriting the original
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Generate a cache-busting timestamp for the image URL
        timestamp = int(time.time())
        
        return JsonResponse({
            'success': True,
            'message': 'Image saved successfully',
            'timestamp': timestamp
        })
        
    except Exception as e:
        print(f"Error saving edited image: {str(e)}")
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })
