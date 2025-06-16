import gradio as gr
import os
from emotion import detect_emotion
import pandas as pd

def process_image(image):
    # If no image was provided, return empty results
    if image is None:
        return None, "Please upload an image", None
        
    # Save the uploaded image temporarily
    temp_path = "temp_upload.jpg"
    image.save(temp_path)
    
    # Analyze the image
    try:
        results = detect_emotion(temp_path)
        
        # Clean up the results for display
        emotion_data = results[0]['emotion']
        age = results[0]['age']
        
        # Create a DataFrame for emotions
        emotion_df = pd.DataFrame({
            'Emotion': list(emotion_data.keys()),
            'Confidence': list(emotion_data.values())
        })
        emotion_df = emotion_df.sort_values('Confidence', ascending=False)
        
        # Format the results text
        dominant_emotion = results[0]['dominant_emotion']
        results_text = f"Dominant Emotion: {dominant_emotion}\nAge: {age}"
    except Exception as e:
        results_text = f"Error processing image: {str(e)}"
        emotion_df = None
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    return image, results_text, emotion_df

# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="DeepFace Analyzer") as demo:
    gr.Markdown("# DeepFace Emotion and Age Analyzer")
    gr.Markdown("Upload an image to analyze the person's emotion and age.")
    
    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(type="pil", label="Upload Image")
            analyze_btn = gr.Button("Analyze", variant="primary")
        
        with gr.Column(scale=1):
            output_image = gr.Image(type="pil", label="Processed Image")
            results = gr.Textbox(label="Analysis Results")
    
    with gr.Row():
        emotion_table = gr.DataFrame(label="Emotion Confidence Scores")
    
    analyze_btn.click(
        fn=process_image,
        inputs=[input_image],
        outputs=[output_image, results, emotion_table]
    )
    
    # Fix: Remove the problematic examples section or set cache_examples to False
    # Instead of using examples with hardcoded file paths, we'll only rely on user uploads
    gr.Examples(
        examples=[],  # No examples for now, as the file path was causing issues
        inputs=input_image,
        outputs=[output_image, results, emotion_table],
        fn=process_image,
        cache_examples=False,  # Set cache_examples to False to avoid file access issues
    )

if __name__ == "__main__":
    demo.launch(show_error=True)  # Added show_error=True to display detailed error messages
