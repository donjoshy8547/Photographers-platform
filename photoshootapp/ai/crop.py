import sys
import os
import time

# Add the path to the face module
current_dir = os.path.dirname(os.path.abspath(__file__))
face_module_path = os.path.join(current_dir, 'face', 'repeted_cropped')
sys.path.append(face_module_path)

# Print debug information
print(f"Current directory: {current_dir}")
print(f"Face module path: {face_module_path}")
print(f"Path exists: {os.path.exists(face_module_path)}")
print(f"Python path: {sys.path}")

try:
    # Import face detection functions
    from face.repeted_cropped import find_repeated_faces, get_face_groups, select_random_faces_from_groups, label_face_group
    print("Successfully imported face module")
except ImportError as e:
    print(f"Error importing face module: {e}")
    # Try to list files in the directory
    if os.path.exists(face_module_path):
        print(f"Files in face module directory: {os.listdir(os.path.join(current_dir, 'face'))}")
    else:
        print("Face module directory does not exist")

# CONFIGURATION - Default values, but these will be overridden by parameters
IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'photos')  # Default path
MIN_FACES = 2      # Minimum occurrences to consider a face as repeated
TOLERANCE = 0.4   # Lower values make face matching more strict (0.0-1.0)

def detect_faces(image_folder=IMAGE_FOLDER, min_faces=MIN_FACES, tolerance=TOLERANCE):
    """
    Wrapper function for finding repeated faces in images
    
    Args:
        image_folder: Path to folder containing images
        min_faces: Minimum occurrences to consider a face as repeated
        tolerance: Lower values make face matching more strict (0.0-1.0)
    
    Returns:
        List of detected faces with their information
    """
    print(f"\n{'='*60}")
    print(f"FACE DETECTION PROCESS STARTED")
    print(f"{'='*60}")
    print(f"Processing images in: {image_folder}")
    print(f"Parameters: min_faces={min_faces}, tolerance={tolerance}")
    
    # Count total images to process
    image_files = [f for f in os.listdir(image_folder) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
    total_images = len(image_files)
    
    if total_images == 0:
        print(f"No images found in {image_folder}")
        return []
    
    print(f"Found {total_images} images to process")
    print(f"Starting face detection...")
    print(f"{'='*60}")
    
    # Add a hook to monitor progress
    def progress_callback(current_image, total, filename, faces_found):
        percent = int((current_image / total) * 100)
        progress_bar = "█" * (percent // 5) + "░" * (20 - (percent // 5))
        print(f"[{progress_bar}] {percent}% | Image {current_image}/{total} | {filename}")
        if faces_found:
            print(f"  • Detected {len(faces_found)} faces in this image")
        else:
            print(f"  • No faces detected in this image")
    
    # Call the original function with our callback
    start_time = time.time()
    results = find_repeated_faces(image_folder, min_faces, tolerance, progress_callback)
    processing_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print(f"FACE DETECTION COMPLETED")
    print(f"{'='*60}")
    print(f"Processing time: {processing_time:.2f} seconds")
    
    if results:
        print(f"Found {len(results)} faces that appear in at least {min_faces} images")
        print(f"\nFace detection results:")
        for i, (path, caption) in enumerate(results):
            print(f"  {i+1}. {os.path.basename(path)}: {caption}")
    else:
        print(f"No faces found in {image_folder} that meet the criteria (min faces: {min_faces}, tolerance: {tolerance})")
    
    output_dir = os.path.join(os.path.dirname(__file__), 'face', 'repeted_cropped', 'detected_faces')
    print(f"\nFaces saved to: {output_dir}")
    print(f"{'='*60}")
    
    return results

def list_face_groups():
    """
    List all detected face groups
    
    Returns:
        List of face groups
    """
    print(f"\n{'='*60}")
    print(f"LISTING FACE GROUPS")
    print(f"{'='*60}")
    
    groups = get_face_groups()
    
    if groups:
        print(f"Found {len(groups)} face groups:")
        for i, group in enumerate(groups):
            print(f"  Group {i+1}: {group}")
    else:
        print("No face groups found. Process images first.")
    
    print(f"{'='*60}")
    return groups

def select_random_faces():
    """
    Select one random face from each detected group
    
    Returns:
        Tuple of (message, selected_faces)
    """
    print(f"\n{'='*60}")
    print(f"SELECTING RANDOM FACES FROM GROUPS")
    print(f"{'='*60}")
    
    start_time = time.time()
    message, selected = select_random_faces_from_groups()
    processing_time = time.time() - start_time
    
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"{message}")
    
    if selected:
        print(f"Selected {len(selected)} random faces:")
        for i, (path, caption) in enumerate(selected):
            print(f"  {i+1}. {os.path.basename(path)}: {caption}")
        
        output_dir = os.path.join(os.path.dirname(__file__), 'face', 'repeted_cropped', 'random_selection')
        print(f"\nRandom faces saved to: {output_dir}")
    else:
        print("No faces were selected. Process images first.")
    
    print(f"{'='*60}")
    return message, selected

def set_face_label(group_display, label_text):
    """
    Label a face group with a name
    
    Args:
        group_display: The group display text (e.g., "Group 1: (3 faces)")
        label_text: Label to assign to the group
    
    Returns:
        Message with the result of the operation
    """
    result = label_face_group(group_display, label_text)
    print(result)
    return result

# Main execution - Choose which function to run by uncommenting
if __name__ == "__main__":
    # Run face detection with default settings
    detect_faces()
    
    # List face groups
    list_face_groups()
    
    # Select random faces from each group
    select_random_faces()
    
    # Label a specific face group (uncomment and edit parameters)
    # set_face_label("Group 1: (3 faces)", "John Doe")
