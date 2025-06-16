from deepface import DeepFace
import os
import traceback
import tensorflow as tf

def detect_emotion(img_path):
    try:
        # Set TensorFlow logging level to suppress warnings
        tf.get_logger().setLevel('ERROR')
        
        # Use enforce_detection=False to prevent errors when face detection fails
        # Remove unsupported parameters (emotion_model_name and age_model_name)
        analysis = DeepFace.analyze(
            img_path=img_path, 
            actions=['emotion', 'age'],
            enforce_detection=False,
            detector_backend='opencv'
        )
        
        # DeepFace might return a list or a single result
        if isinstance(analysis, list):
            if not analysis:  # Empty list
                print(f"No face detected in: {os.path.basename(img_path)}")
                return None
                
            # If we have multiple faces, use the one with highest confidence or the first one
            if len(analysis) > 1:
                print(f"Found {len(analysis)} faces in the image, using the most prominent one")
            
            face_data = analysis[0]  # Use the first face (most prominent)
        else:
            face_data = analysis
        
        # Extracting emotion with the highest percentage
        dominant_emotion = face_data.get('dominant_emotion', 'Unknown')
        age = face_data.get('age', 0)
        emotion_scores = face_data.get('emotion', {})
        
        # Convert emotion scores to percentages if they're not already
        if emotion_scores:
            emotion_scores = {k: float(v) for k, v in emotion_scores.items()}
        
        # Return both the dominant emotion and the full emotion scores
        return {
            "dominant_emotion": dominant_emotion, 
            "age": age,
            "emotion": emotion_scores  # This contains all emotion scores
        }
    except Exception as e:
        print(f"Error in detect_emotion: {str(e)}")
        traceback.print_exc()
        
        # Try with different backend as a fallback
        try:
            print("Trying with different settings...")
            analysis = DeepFace.analyze(
                img_path=img_path, 
                actions=['emotion', 'age'],
                enforce_detection=False,
                detector_backend='retinaface'
            )
            
            if isinstance(analysis, list) and analysis:
                face_data = analysis[0]
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

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        result = detect_emotion(img_path)
        print(result)
    else:
        print("Please provide an image path as argument")
