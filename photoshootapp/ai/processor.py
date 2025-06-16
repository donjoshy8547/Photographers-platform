import os
import sys
import threading
import time
import traceback
import csv
import shutil
from PIL import Image, ImageDraw

# Add necessary paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)  # Add the project root to path
sys.path.append(current_dir)  # Add the current directory to path

# Debug information
print(f"Current directory: {current_dir}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path}")

# Add combined AI models path
combined_ai_path = r"C:\Users\donjo\CascadeProjects\combined-ai-models"
if os.path.exists(combined_ai_path):
    sys.path.append(combined_ai_path)
    print(f"Added combined AI models path to sys.path: {combined_ai_path}")
    print(f"Files in combined AI models directory: {os.listdir(combined_ai_path)}")
else:
    print(f"Warning: Combined AI models directory not found: {combined_ai_path}")

# Add face detection directory
face_dir = os.path.join(current_dir, 'face', 'repeted_cropped')
if os.path.exists(face_dir):
    sys.path.append(face_dir)
    print(f"Added face directory to path: {face_dir}")
    print(f"Files in face directory: {os.listdir(face_dir)}")
else:
    print(f"Warning: Face directory not found: {face_dir}")
    os.makedirs(face_dir, exist_ok=True)
    print(f"Created face directory: {face_dir}")

# Valid image extensions
valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

def process_images(input_directory, output_csv=None, min_faces=2, tolerance=0.5):
    """
    Process images using both integrated_model.py and crop.py in sequence
    
    Args:
        input_directory: Directory containing images to process
        output_csv: Path to save caption/emotion results
        min_faces: Minimum occurrences to consider a face as repeated
        tolerance: Matching tolerance - lower values are stricter (0.0-1.0)
    
    Returns:
        Dictionary with processing results
    """
    results = {
        'status': 'success',
        'message': 'Processing completed successfully',
        'faces_detected': 0,
        'face_groups': 0,
        'integrated_model_status': 'not_run',
        'face_detection_status': 'not_run',
        'details': {}
    }
    
    try:
        print(f"\n=== AI PROCESSOR: STARTING IMAGE PROCESSING ===")
        print(f"Input Directory: {input_directory}")
        print(f"Output CSV: {output_csv}")
        print(f"Min faces: {min_faces}")
        print(f"Tolerance: {tolerance}")
        
        # Validate input directory
        if not os.path.exists(input_directory):
            print(f"Error: Input directory '{input_directory}' does not exist.")
            os.makedirs(input_directory, exist_ok=True)
            print(f"Created empty directory. Please add images to this folder.")
            results['status'] = 'error'
            results['message'] = f"Input directory does not exist: {input_directory}"
            return results
            
        # Check if input directory exists
        if not os.path.exists(input_directory):
            print(f"Error: Input directory does not exist: {input_directory}")
            # Create the directory
            os.makedirs(input_directory, exist_ok=True)
            print(f"Created input directory: {input_directory}")
            # Return error message
            return {
                'status': 'error',
                'message': f"Input directory not found and was created: {input_directory}. Please add images to this directory."
            }
        
        # Count images in the input directory
        image_count = 0
        for filename in os.listdir(input_directory):
            if filename.lower().endswith(valid_extensions):
                image_count += 1
        
        print(f"Found {image_count} images in {input_directory}")
        
        if image_count == 0:
            print(f"Error: No images found in {input_directory}")
            # Create a sample image for testing
            sample_image_path = os.path.join(input_directory, 'sample_image.jpg')
            try:
                # Create a simple test image using PIL if available
                try:
                    from PIL import Image, ImageDraw
                    
                    # Create a blank image with a white background
                    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
                    d = ImageDraw.Draw(img)
                    
                    # Draw some text and shapes
                    d.text((300, 200), "Sample Test Image", fill=(0, 0, 0))
                    d.rectangle([(200, 100), (600, 500)], outline=(0, 0, 0))
                    
                    # Save the image
                    img.save(sample_image_path)
                    print(f"Created sample test image: {sample_image_path}")
                    
                    # Update image count
                    image_count = 1
                except ImportError:
                    print("PIL not available, cannot create sample image")
                    # Create an empty file as a placeholder
                    with open(sample_image_path, 'w') as f:
                        f.write("This is a placeholder for a sample image.")
                    print(f"Created placeholder file: {sample_image_path}")
                    
                    return {
                        'status': 'error',
                        'message': f"No images found in {input_directory}. A placeholder file was created, but real images are needed for processing."
                    }
            except Exception as e:
                print(f"Error creating sample image: {e}")
                return {
                    'status': 'error',
                    'message': f"No images found in {input_directory} and could not create sample image: {str(e)}"
                }
        
        # Set default output CSV if not provided
        if not output_csv:
            output_csv = os.path.join(current_dir, "image_captions.csv")
        
        # =========== STEP 1: Run integrated model ===========
        print(f"\n===== STEP 1: Running Caption and Emotion Detection =====")
        
        # Make sure the directory exists
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        print(f"Ensured output directory exists: {os.path.dirname(output_csv)}")
        
        # Run the full directory processing
        print("\nProcessing all images with integrated_model.py...")
        success = process_images_directory(input_directory, output_csv)
        
        if success:
            results['integrated_model_status'] = 'success'
        else:
            results['integrated_model_status'] = 'warning'
            results['message'] = "Integrated model processing completed with warnings"
        
        # Verify the CSV was created
        if os.path.exists(output_csv):
            # Count the number of entries in the CSV
            row_count = 0
            with open(output_csv, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    row_count += 1
            
            print(f"\n=== AI PROCESSOR: PROCESSING COMPLETE ===")
            print(f"CSV file created at: {output_csv}")
            print(f"Processed {row_count} images successfully")
        else:
            print(f"\n=== AI PROCESSOR: WARNING ===")
            print(f"Processing completed but no CSV file was created at {output_csv}")
            results['status'] = 'warning'
            results['message'] = "Integrated model did not create output file"
            results['integrated_model_status'] = 'failed'
        
        # =========== STEP 2: Run face detection ===========
        print(f"\n===== STEP 2: Running Face Detection =====")
        print(f"Parameters: min_faces={min_faces}, tolerance={tolerance}")
        
        try:
            # Import face detection functions
            print("Importing crop.py...")
            from crop import detect_faces, list_face_groups, select_random_faces, set_face_label
            
            # Run face detection
            print("\nRunning face detection...")
            faces = detect_faces(input_directory, min_faces, tolerance)
            
            if faces:
                results['faces_detected'] = len(faces)
                print(f"Found {len(faces)} faces in {input_directory}")
                
                # Test list_face_groups
                print("\nListing face groups...")
                face_groups = list_face_groups()
                
                if face_groups:
                    results['face_groups'] = len(face_groups)
                    print(f"Found {len(face_groups)} face groups")
                    
                    # Test select_random_faces
                    print("\nSelecting random faces...")
                    message, selected = select_random_faces()
                    
                    if selected:
                        results['random_faces'] = len(selected)
                        print(f"Selected {len(selected)} random faces")
                        
                        # Verify random selection directory
                        random_dir = os.path.join(current_dir, 'face', 'repeted_cropped', 'random_selection')
                        if os.path.exists(random_dir):
                            random_files = [f for f in os.listdir(random_dir) if f.lower().endswith(valid_extensions)]
                            print(f"Found {len(random_files)} random face images in {random_dir}")
                            
                            # Copy face images to media directory for web display
                            media_random_dir = os.path.join(media_root, 'ai', 'face', 'repeted_cropped', 'random_selection')
                            os.makedirs(media_random_dir, exist_ok=True)
                            print(f"Copying face images to media directory: {media_random_dir}")
                            
                            # Copy each face image
                            for face_file in random_files:
                                src_path = os.path.join(random_dir, face_file)
                                dst_path = os.path.join(media_random_dir, face_file)
                                try:
                                    shutil.copy2(src_path, dst_path)
                                    print(f"Copied {face_file} to media directory")
                                except Exception as e:
                                    print(f"Error copying {face_file}: {str(e)}")
                
                results['face_detection_status'] = 'success'
            else:
                print(f"No faces found in {input_directory} that meet the criteria")
                results['face_detection_status'] = 'no_faces'
            
        except Exception as e:
            print(f"\n=== AI PROCESSOR: ERROR ===")
            print(f"Error in face detection: {str(e)}")
            traceback.print_exc()
            results['face_detection_status'] = 'failed'
            if results['status'] == 'success':  # Don't overwrite earlier errors
                results['status'] = 'partial'
                results['message'] = f"Captions generated, but face detection failed: {str(e)}"
        
        print("\n====== AI PROCESSING WORKFLOW COMPLETE ======")
        print(f"Status: {results['status']}")
        print(f"Integrated Model: {results['integrated_model_status']}")
        print(f"Face Detection: {results['face_detection_status']}")
        print(f"Faces Detected: {results['faces_detected']}")
        print(f"Face Groups: {results['face_groups']}")
        
    except Exception as e:
        print(f"\n=== AI PROCESSOR: ERROR ===")
        print(f"Error processing images: {str(e)}")
        traceback.print_exc()
        results['status'] = 'error'
        results['message'] = f"Error processing images: {str(e)}"
    
    return results

def process_images_directory(input_directory, output_csv):
    """
    Process all images in a directory using the integrated model
    
    Args:
        input_directory: Directory containing images to process
        output_csv: Path to save caption/emotion results
    
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        # Import the integrated model
        sys.path.append(project_root)
        from integrated_model import process_directory
        
        # Process the directory
        print(f"\n=== AI PROCESSOR: PROCESSING DIRECTORY ===")
        print(f"Processing directory: {input_directory}")
        print(f"Output CSV: {output_csv}")
        
        # Make sure output directory exists
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        print(f"Ensured output directory exists: {os.path.dirname(output_csv)}")
        
        # Run the processing
        print(f"Starting integrated model processing...")
        process_directory(input_directory, output_csv)
        
        # Verify the CSV was created
        if os.path.exists(output_csv):
            # Count the number of entries in the CSV
            row_count = 0
            with open(output_csv, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    row_count += 1
            
            print(f"\n=== AI PROCESSOR: PROCESSING COMPLETE ===")
            print(f"CSV file created at: {output_csv}")
            print(f"Processed {row_count} images successfully")
            return True
        else:
            print(f"\n=== AI PROCESSOR: WARNING ===")
            print(f"Processing completed but no CSV file was created at {output_csv}")
            return False
            
    except Exception as e:
        print(f"\n=== AI PROCESSOR: ERROR ===")
        print(f"Error processing images: {str(e)}")
        traceback.print_exc()
        return False

def web_interface_process(photographer_id, image_paths=None):
    """
    Process images for a specific photographer through the web interface
    
    Args:
        photographer_id: ID of the photographer
        image_paths: Optional list of specific image paths to process
    
    Returns:
        Dictionary with processing results
    """
    print(f"\n====== STARTING AI PROCESSING FOR PHOTOGRAPHER {photographer_id} ======")
    
    # Import Django settings to get media paths
    try:
        from django.conf import settings
        media_root = settings.MEDIA_ROOT
        print(f"Media root: {media_root}")
    except ImportError:
        print("Warning: Could not import Django settings, using default paths")
        # Default media root
        media_root = os.path.join(project_root, 'media')
    
    # Define output paths
    output_dir = os.path.join(media_root, 'ai', str(photographer_id))
    output_csv = os.path.join(output_dir, 'image_captions.csv')
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Print paths for debugging
    print(f"Output directory: {output_dir}")
    print(f"Output CSV: {output_csv}")
    
    # If no specific image paths provided, use the default directory
    if image_paths is None:
        input_directory = os.path.join(media_root, f'photos/photographer_{photographer_id}')
        print(f"No specific image paths provided, using input directory: {input_directory}")
        
        # Check if input directory exists
        if not os.path.exists(input_directory):
            print(f"Error: Input directory does not exist: {input_directory}")
            return {
                'status': 'error',
                'message': f"Input directory not found: {input_directory}"
            }
        
        # Count images in the input directory
        image_count = 0
        image_paths = []
        for filename in os.listdir(input_directory):
            if filename.lower().endswith(valid_extensions):
                image_count += 1
                image_paths.append(os.path.join(input_directory, filename))
        
        if image_count == 0:
            print(f"Error: No images found in {input_directory}")
            return {
                'status': 'error',
                'message': f"No images found in {input_directory}"
            }
        
        print(f"Found {image_count} images to process in directory")
    else:
        # Use the provided image paths
        image_count = len(image_paths)
        print(f"Using {image_count} provided image paths")
        
        if image_count == 0:
            return {
                'status': 'error',
                'message': "No images provided for processing"
            }
    
    # Initialize results dictionary
    results = {
        'status': 'success',
        'message': f"Successfully processed {image_count} images",
        'processed_images': image_count,
        'output_csv': output_csv
    }
    
    try:
        # Process the images
        print(f"Processing {image_count} images...")
        
        # Create the CSV file with headers
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['image_path', 'caption', 'emotion', 'age', 'gender', 'race'])
        
        # Process each image
        for i, image_path in enumerate(image_paths):
            try:
                print(f"Processing image {i+1}/{image_count}: {image_path}")
                
                # Process the image
                caption, emotion, age, gender, race = process_image(image_path)
                
                # Write the results to the CSV
                with open(output_csv, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([image_path, caption, emotion, age, gender, race])
                
                print(f"Processed image {i+1}/{image_count}")
            except Exception as e:
                print(f"Error processing image {image_path}: {str(e)}")
                traceback.print_exc()
                # Still write to CSV with error information
                try:
                    with open(output_csv, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([image_path, f"Error: {str(e)}", "error", "", "", ""])
                except Exception as write_error:
                    print(f"Error writing to CSV: {str(write_error)}")
        
        print(f"Finished processing {image_count} images")
        
        # =========== STEP 2: Run face detection ===========
        print(f"\n===== STEP 2: Running Face Detection =====")
        
        # Determine input directory for face detection
        if 'input_directory' not in locals():
            # If we're using specific image paths, get the directory from the first image
            if image_paths and len(image_paths) > 0:
                input_directory = os.path.dirname(image_paths[0])
                print(f"Using directory from first image: {input_directory}")
            else:
                input_directory = os.path.join(media_root, f'photos/photographer_{photographer_id}')
                print(f"Using default directory: {input_directory}")
        
        print(f"Input directory: {input_directory}")
        
        # Set face detection parameters
        min_faces = 2
        tolerance = 0.5
        print(f"Parameters: min_faces={min_faces}, tolerance={tolerance}")
        
        try:
            # Import face detection functions
            print("Importing crop.py...")
            from crop import detect_faces, list_face_groups, select_random_faces
            
            # Run face detection
            print("\nRunning face detection...")
            faces = detect_faces(input_directory, min_faces, tolerance)
            
            if faces:
                results['faces_detected'] = len(faces)
                print(f"Found {len(faces)} faces in {input_directory}")
                
                # List face groups
                print("\nListing face groups...")
                face_groups = list_face_groups()
                
                if face_groups:
                    results['face_groups'] = len(face_groups)
                    print(f"Found {len(face_groups)} face groups")
                    
                    # Select random faces
                    print("\nSelecting random faces...")
                    message, selected = select_random_faces()
                    
                    if selected:
                        results['random_faces'] = len(selected)
                        print(f"Selected {len(selected)} random faces")
                        
                        # Verify random selection directory
                        random_dir = os.path.join(current_dir, 'face', 'repeted_cropped', 'random_selection')
                        if os.path.exists(random_dir):
                            random_files = [f for f in os.listdir(random_dir) if f.lower().endswith(valid_extensions)]
                            print(f"Found {len(random_files)} random face images in {random_dir}")
                            
                            # Copy face images to media directory for web display
                            media_random_dir = os.path.join(media_root, 'ai', 'face', 'repeted_cropped', 'random_selection')
                            os.makedirs(media_random_dir, exist_ok=True)
                            print(f"Copying face images to media directory: {media_random_dir}")
                            
                            # Copy each face image
                            for face_file in random_files:
                                src_path = os.path.join(random_dir, face_file)
                                dst_path = os.path.join(media_random_dir, face_file)
                                try:
                                    shutil.copy2(src_path, dst_path)
                                    print(f"Copied {face_file} to media directory")
                                except Exception as e:
                                    print(f"Error copying {face_file}: {str(e)}")
                
                results['face_detection_status'] = 'success'
            else:
                print(f"No faces found in {input_directory} that meet the criteria")
                results['face_detection_status'] = 'no_faces'
            
        except Exception as e:
            print(f"\n=== AI PROCESSOR: ERROR ===")
            print(f"Error in face detection: {str(e)}")
            traceback.print_exc()
            results['face_detection_status'] = 'failed'
        
        return results
    except Exception as e:
        print(f"Error in web_interface_process: {str(e)}")
        traceback.print_exc()
        return {
            'status': 'error',
            'message': f"Error processing images: {str(e)}"
        }

def process_images_async(input_directory, output_csv=None, min_faces=2, tolerance=0.5):
    """
    Run image processing in a background thread
    
    Args:
        input_directory: Directory containing images to process
        output_csv: Path to save caption/emotion results
        min_faces: Minimum occurrences to consider a face as repeated
        tolerance: Matching tolerance - lower values are stricter (0.0-1.0)
    
    Returns:
        Thread object that's running the processing
    """
    print(f"Starting asynchronous AI processing for {input_directory}")
    thread = threading.Thread(
        target=process_images,
        args=(input_directory, output_csv, min_faces, tolerance)
    )
    thread.daemon = True
    thread.start()
    print(f"Background processing thread started")
    return thread

def verify_ai_modules():
    """
    Verify that all AI modules are available and can be imported
    
    Returns:
        Dictionary with module verification results
    """
    results = {
        'integrated_model': False,
        'crop': False,
        'face': False
    }
    
    print("Verifying AI modules...")
    
    # Check integrated_model.py
    try:
        import integrated_model
        results['integrated_model'] = True
        print("[OK] integrated_model.py is available")
    except Exception as e:
        print(f"[ERROR] integrated_model.py error: {str(e)}")
    
    # Check crop.py
    try:
        import crop
        results['crop'] = True
        print("[OK] crop.py is available")
    except Exception as e:
        print(f"[ERROR] crop.py error: {str(e)}")
    
    # Check face module
    try:
        sys.path.append(face_dir)
        import face
        results['face'] = True
        print("[OK] face module is available")
    except Exception as e:
        print(f"[ERROR] face module error: {str(e)}")
    
    return results

def process_image(image_path):
    """
    Process a single image using the AI models
    
    Args:
        image_path: Path to the image file
        
    Returns:
        tuple: (caption, emotion, age, gender, race)
    """
    print(f"Processing image: {image_path}")
    
    try:
        # Check if the image file exists
        if not os.path.exists(image_path):
            print(f"Warning: Image file does not exist: {image_path}")
            return "Image not found", "unknown", "unknown", "unknown", "unknown"
        
        # Initialize default values
        caption = ""
        emotion = ""
        age = ""
        gender = ""
        race = ""
        
        # Load the image
        image = Image.open(image_path)
        
        # Generate caption using BLIP model
        caption = generate_caption(image)
        print(f"Generated caption: {caption}")
        
        # Analyze face for emotion, age, gender, and race
        try:
            face_analysis = analyze_face(image_path)
            if face_analysis:
                emotion = face_analysis.get('emotion', '')
                age = face_analysis.get('age', '')
                gender = face_analysis.get('gender', '')
                race = face_analysis.get('race', '')
                print(f"Face analysis: emotion={emotion}, age={age}, gender={gender}, race={race}")
        except Exception as e:
            print(f"Face analysis failed: {str(e)}")
            # Continue with just the caption if face analysis fails
        
        return caption, emotion, age, gender, race
    except Exception as e:
        print(f"Error processing image {image_path}: {str(e)}")
        traceback.print_exc()
        return "Error", "", "", "", ""

def generate_caption(image):
    """
    Generate a caption for an image using the BLIP model
    
    Args:
        image: PIL Image object
        
    Returns:
        str: Generated caption
    """
    try:
        # Import the necessary modules
        from transformers import BlipProcessor, BlipForConditionalGeneration
        
        # Load the BLIP model
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
        
        # Process the image
        inputs = processor(image, return_tensors="pt")
        
        # Generate the caption
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        return caption
    except Exception as e:
        print(f"Error generating caption: {str(e)}")
        traceback.print_exc()
        return "Caption generation failed"

def analyze_face(image_path):
    """
    Analyze a face in an image using DeepFace
    
    Args:
        image_path: Path to the image file
        
    Returns:
        dict: Face analysis results
    """
    try:
        # Import DeepFace
        from deepface import DeepFace
        
        # Analyze the face
        analysis = DeepFace.analyze(img_path=image_path, actions=['emotion', 'age', 'gender', 'race'], enforce_detection=False)
        
        # If multiple faces are detected, use the first one
        if isinstance(analysis, list):
            analysis = analysis[0]
        
        # Extract the dominant emotion
        emotion = max(analysis['emotion'].items(), key=lambda x: x[1])[0]
        
        # Extract the dominant gender
        dominant_gender = max(analysis['gender'].items(), key=lambda x: x[1])[0]
        
        # Create a simplified result dictionary
        result = {
            'emotion': emotion,
            'age': str(analysis['age']),
            'gender': dominant_gender,
            'race': max(analysis['race'].items(), key=lambda x: x[1])[0]
        }
        
        return result
    except Exception as e:
        print(f"Face analysis failed: {str(e)}")
        traceback.print_exc()
        return None

def main():
    """
    Main entry point for the script when run from command line
    Parses arguments and calls the appropriate processing function
    """
    import argparse
    
    # Check if this is being called directly from another script
    if len(sys.argv) == 1:
        # No arguments provided, assume being called from web interface
        print("No command line arguments provided, assuming direct call from web interface")
        
        # Check if we're being imported by another module (like views.py)
        if __name__ != "__main__":
            print("Module imported by another script, not executing main function")
            return 0
            
        # For testing direct execution without arguments
        # In production, this would be called with the photographer_id from views.py
        print("Direct execution without arguments - for testing only")
        return 0
    
    # Handle --photographer-id argument for direct web interface calls
    if len(sys.argv) == 3 and sys.argv[1] == "--photographer-id":
        photographer_id = sys.argv[2]
        print(f"Processing images for photographer ID: {photographer_id}")
        result = web_interface_process(photographer_id)
        if result['status'] == 'success':
            print("Processing completed successfully")
            return 0
        else:
            print(f"Processing completed with status: {result['status']}")
            print(f"Message: {result['message']}")
            return 1
    
    # Standard command-line argument parsing
    parser = argparse.ArgumentParser(description='Process images with AI models')
    parser.add_argument('--input', required=True, help='Directory containing images to process')
    parser.add_argument('--output', help='Path to save caption/emotion results')
    parser.add_argument('--min-faces', type=int, default=2, help='Minimum occurrences to consider a face as repeated')
    parser.add_argument('--tolerance', type=float, default=0.5, help='Face matching tolerance (0.0-1.0)')
    parser.add_argument('--async', action='store_true', help='Run processing asynchronously')
    
    args = parser.parse_args()
    
    # Verify input directory exists
    if not os.path.exists(args.input):
        print(f"Error: Input directory '{args.input}' does not exist")
        return 1
    
    # Run processing
    if getattr(args, 'async', False):
        thread = process_images_async(args.input, args.output, args.min_faces, args.tolerance)
        print(f"Processing started in background thread. Check logs for progress.")
        return 0
    else:
        results = process_images(args.input, args.output, args.min_faces, args.tolerance)
        if results['status'] == 'success':
            print("Processing completed successfully")
            return 0
        else:
            print(f"Processing completed with status: {results['status']}")
            print(f"Message: {results['message']}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
