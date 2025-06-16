from PIL import Image
import os
import csv
from transformers import BlipProcessor, BlipForConditionalGeneration


processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

def generate_caption(img_path):
    img_input = Image.open(img_path).convert('RGB')
    inputs = processor(img_input, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption


def process_images_directory(input_dir, output_csv):
    # Create a list to store results
    results = []
    
    # Process each image in the directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            img_path = os.path.join(input_dir, filename)
            try:
                caption = generate_caption(img_path)
                results.append([img_path, caption])  # Store full path instead of just filename
                print(f"Processed {img_path}: {caption}")
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
    
    # Save results to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Image Path', 'Caption'])  # Updated header
        csv_writer.writerows(results)
    
    print(f"Results saved to {output_csv}")


if __name__ == "__main__":
    # Set your input directory containing images and output CSV file path
    input_directory = r"F:\photoshootapp\photoshootapp\photoshootapp\media\media"  # Use raw string with r prefix
    output_csv_file = "image_captions.csv"
    
    # Create the images directory if it doesn't exist
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)
        print(f"Created directory '{input_directory}'. Please add your images to this folder.")
    
    # Process the images
    process_images_directory(input_directory, output_csv_file)