# Integrated Model - Combines BLIP for image captioning and DeepFace for emotion detection
import sys
import os
import csv
from PIL import Image
import time
import traceback

# Add paths to required modules
current_dir = os.path.dirname(os.path.abspath(__file__))
deepface_path = os.path.join(current_dir, 'ai', 'deppface-test')
blip_path = os.path.join(current_dir, 'ai', 'blip-test')

# Add paths to sys.path for imports
sys.path.append(deepface_path)
sys.path.append(blip_path)

# Initialize flags for available models
has_emotion_detection = False
has_caption_generation = False

# Try to import emotion detection
try:
    print("Attempting to import emotion detection...")
    from emotion import detect_emotion
    has_emotion_detection = True
    print("Successfully imported emotion detection")
except Exception as e:
    print(f"Error importing emotion detection: {e}")
    
    # Create a fallback implementation of detect_emotion
    def detect_emotion(img_path):
        """
        Detect emotions and age in an image using DeepFace
        
        Args:
            img_path: Path to the image file
        
        Returns:
            Dictionary containing dominant_emotion, age, and emotion scores
            or None if no face was detected
        """
        try:
            # Try to import DeepFace
            from deepface import DeepFace
            import traceback
            import tensorflow as tf
            
            # Set TensorFlow logging level to suppress warnings
            tf.get_logger().setLevel('ERROR')
            
            print(f"Analyzing face with DeepFace directly: {os.path.basename(img_path)}")
            
            # Check if the file exists and is readable
            if not os.path.exists(img_path):
                print(f"File not found: {img_path}")
                return None
            
            # First attempt with OpenCV detector
            try:
                # Remove unsupported parameters (emotion_model_name and age_model_name)
                face_analysis = DeepFace.analyze(
                    img_path=img_path, 
                    actions=['emotion', 'age'],
                    enforce_detection=False,
                    detector_backend='opencv'
                )
                
                # Handle empty results
                if isinstance(face_analysis, list) and not face_analysis:
                    print(f"No face detected with OpenCV detector, trying SSD detector")
                    
                    # Try again with SSD detector
                    face_analysis = DeepFace.analyze(
                        img_path=img_path, 
                        actions=['emotion', 'age'],
                        enforce_detection=False,
                        detector_backend='ssd'
                    )
                    
                    if isinstance(face_analysis, list) and not face_analysis:
                        print(f"No face detected with SSD detector either")
                        return None
                
                # Process the results
                if isinstance(face_analysis, list):
                    if len(face_analysis) > 1:
                        print(f"Found {len(face_analysis)} faces, using the most prominent one")
                    face_data = face_analysis[0]
                else:
                    face_data = face_analysis
                
                # Extract emotion and age data
                dominant_emotion = face_data.get('dominant_emotion', 'Unknown')
                age = face_data.get('age', 0)
                emotion_scores = face_data.get('emotion', {})
                
                # Ensure emotion scores are floats
                if emotion_scores:
                    emotion_scores = {k: float(v) for k, v in emotion_scores.items()}
                
                print(f"Face analysis successful: {dominant_emotion}, Age: {age}")
                
                return {
                    'dominant_emotion': dominant_emotion,
                    'age': age,
                    'emotion': emotion_scores
                }
            except Exception as e:
                print(f"DeepFace analysis failed: {str(e)}")
                traceback.print_exc()
                
                # Try one more time with different backend and settings
                try:
                    print("Trying with different settings...")
                    face_analysis = DeepFace.analyze(
                        img_path=img_path, 
                        actions=['emotion', 'age'],
                        enforce_detection=False,
                        detector_backend='retinaface'
                    )
                    
                    if isinstance(face_analysis, list) and face_analysis:
                        face_data = face_analysis[0]
                        dominant_emotion = face_data.get('dominant_emotion', 'Unknown')
                        age = face_data.get('age', 0)
                        emotion_scores = face_data.get('emotion', {})
                        
                        if emotion_scores:
                            emotion_scores = {k: float(v) for k, v in emotion_scores.items()}
                        
                        print(f"Face analysis successful with alternative settings: {dominant_emotion}, Age: {age}")
                        
                        return {
                            'dominant_emotion': dominant_emotion,
                            'age': age,
                            'emotion': emotion_scores
                        }
                except Exception as e2:
                    print(f"Second attempt also failed: {str(e2)}")
                
                return None
                    
        except Exception as e:
            print(f"Error in detect_emotion: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

# Import BLIP image captioning
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    
    # Initialize BLIP model
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
    
    def generate_caption(img_path):
        img_input = Image.open(img_path).convert('RGB')
        inputs = processor(img_input, return_tensors="pt")
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption
    
    has_caption_generation = True
    print("Successfully initialized BLIP model")
except Exception as e:
    print(f"Error initializing BLIP model: {e}")
    
    # Try to import from main.py if direct import fails
    try:
        sys.path.append(os.path.dirname(blip_path))
        from blip_test.main import generate_caption
        has_caption_generation = True
        print("Successfully imported generate_caption from blip_test.main")
    except Exception as e2:
        print(f"Error importing from main.py: {e2}")
        
        # Define a placeholder function if all imports fail
        def generate_caption(img_path):
            return "Caption generation unavailable"

def process_directory(input_dir, output_csv):
    """
    Process all images in a directory and save results to CSV
    
    Args:
        input_dir: Directory containing images
        output_csv: Path to output CSV file
    """
    # Create a list to store results
    results = []
    
    # Get all image files
    image_files = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_files.append(filename)
    
    total_images = len(image_files)
    print(f"\n=== PROCESSING {total_images} IMAGES ===")
    
    # Define a local process_image function
    def process_image(img_path):
        """
        Process a single image through both BLIP and DeepFace models
        
        Args:
            img_path: Path to the image file
        
        Returns:
            Dictionary containing caption, emotion, age and emotion scores
        """
        filename = os.path.basename(img_path)
        result = {
            'image_path': img_path,
            'caption': 'Unknown',
            'dominant_emotion': 'Unknown',
            'age': 0,
            'emotion_scores': {}
        }
        
        # Generate caption with BLIP
        try:
            print(f"  • Generating caption with BLIP model...")
            start_time = time.time()
            result['caption'] = generate_caption(img_path)
            caption_time = time.time() - start_time
            print(f"  • Caption generated in {caption_time:.2f} seconds: {result['caption']}")
        except Exception as e:
            print(f"  • ERROR generating caption for {filename}: {e}")
            traceback.print_exc()
        
        # Detect emotion and age with DeepFace
        try:
            print(f"  • Analyzing face with DeepFace model...")
            start_time = time.time()
            emotion_result = detect_emotion(img_path)
            emotion_time = time.time() - start_time
            
            if emotion_result:
                result['dominant_emotion'] = emotion_result.get('dominant_emotion', 'Unknown')
                result['age'] = emotion_result.get('age', 0)
                
                # Get the emotion scores dictionary if available
                if 'emotion' in emotion_result and isinstance(emotion_result['emotion'], dict):
                    result['emotion_scores'] = emotion_result['emotion']
                    print(f"  • Face analysis completed in {emotion_time:.2f} seconds")
                    print(f"  • Dominant emotion: {result['dominant_emotion']}")
                    print(f"  • Estimated age: {result['age']}")
                else:
                    # Create empty emotion scores if not available
                    result['emotion_scores'] = {
                        'angry': 0.0, 'disgust': 0.0, 'fear': 0.0, 
                        'happy': 0.0, 'sad': 0.0, 'surprise': 0.0, 'neutral': 0.0
                    }
                    print(f"  • Face analysis completed but no emotion scores available")
            else:
                print(f"  • No face detected in {filename} (or detection failed)")
                print(f"  • Using default values for emotion and age")
        except Exception as e:
            print(f"  • ERROR detecting emotion in {filename}: {str(e)}")
            traceback.print_exc()
            
            # Set default emotion scores
            result['emotion_scores'] = {
                'angry': 0.0, 'disgust': 0.0, 'fear': 0.0, 
                'happy': 0.0, 'sad': 0.0, 'surprise': 0.0, 'neutral': 0.0
            }
        
        return result
    
    # Process each image in the directory
    for i, filename in enumerate(image_files, 1):
        img_path = os.path.join(input_dir, filename)
        print(f"\n[{i}/{total_images}] PROCESSING IMAGE: {filename}")
        print(f"{'='*50}")
        
        try:
            print(f"Step 1: Loading image...")
            
            result = process_image(img_path)
            
            # Print the results
            print(f"Step 2: Results for {filename}:")
            print(f"  - Caption: {result['caption']}")
            print(f"  - Emotion: {result['dominant_emotion']}")
            print(f"  - Age: {result['age']}")
            
            # Print emotion scores if available
            if result['emotion_scores']:
                print(f"  - Emotion scores:")
                for emotion, score in result['emotion_scores'].items():
                    print(f"    * {emotion}: {score:.2f}%")
            
            # Prepare row for CSV
            row = [
                result['image_path'],
                result['caption'],
                result['dominant_emotion'],
                result['age']
            ]
            
            # Add emotion scores if available
            if result['emotion_scores']:
                for emotion in ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']:
                    row.append(result['emotion_scores'].get(emotion, 0))
            else:
                # Add zeros for missing emotion scores
                row.extend([0, 0, 0, 0, 0, 0, 0])
            
            results.append(row)
            print(f"Step 3: Successfully processed {filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            traceback.print_exc()
            # Add a placeholder row for failed images
            results.append([
                img_path,
                f"Error processing image: {str(e)}",
                "Unknown",
                0,
                0, 0, 0, 0, 0, 0, 0  # Placeholder for emotion scores
            ])
    
    # Write results to CSV
    print(f"\n=== WRITING RESULTS TO CSV: {output_csv} ===")
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['Image Path', 'Caption', 'Dominant Emotion', 'Age', 
                           'Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'])
            # Write data rows
            for row in results:
                writer.writerow(row)
        
        print(f"Successfully wrote {len(results)} rows to {output_csv}")
        return True
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        traceback.print_exc()
        return False

# Create an alias for process_directory to match the name used in processor.py
process_images_directory = process_directory

# Test the integrated model with a single image
if __name__ == "__main__":
    # Process a directory of images
    input_directory = r"F:\photoshootapp\photoshootapp\photoshootapp\media\media"  # Replace with your images folder path
    output_csv_file = "F:\photoshootapp\photoshootapp\photoshootapp\integrated_results.csv"
    
    if os.path.exists(input_directory):
        print(f"Processing images in {input_directory}...")
        process_directory(input_directory, output_csv_file)
        print(f"Processing complete! Results saved to {output_csv_file}")
    else:
        print(f"Directory not found: {input_directory}")
        print("Please update the input_directory path in the script.")
    
    # Uncomment to test with a single image
    # test_image = r'F:\face\input\jeff-bezos-2-115933249.jpg'
    # if os.path.exists(test_image):
    #     result = process_image(test_image)
    #     print("\nIntegrated model test result:")
    #     for key, value in result.items():
    #         print(f"{key}: {value}")