import os
import json
import shutil
import sys
from collections import defaultdict
import cv2
import face_recognition

def get_matching_images_for_face(group_id, photographer_directory=None, output_directory=None):
    """
    Retrieve all original images where a particular face group appears.
    
    Args:
        group_id: The ID of the face group to find matches for
        photographer_directory: Path to the photographer's photos directory 
                               (default: None, will use face_groups.json data)
        output_directory: Path to save copies of matching images
                         (default: None, will create a temp directory)
    
    Returns:
        List of tuples (image_path, face_locations) for all images containing faces from the group
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    groups_file = os.path.join(current_dir, "face_groups.json")
    
    # Check if face groups data exists
    if not os.path.exists(groups_file):
        print(f"Face groups data not found: {groups_file}")
        return []
    
    # Load face groups data
    try:
        with open(groups_file, 'r') as f:
            groups_data = json.load(f)
    except Exception as e:
        print(f"Error loading face groups data: {e}")
        return []
    
    # Convert group_id to string if needed
    group_id = str(group_id)
    
    # Check if group exists
    if group_id not in groups_data:
        print(f"Group ID {group_id} not found in face groups data")
        return []
    
    # Get images for this group
    group_images = groups_data[group_id].get('images', [])
    
    if not group_images:
        print(f"No images found for group {group_id}")
        return []
    
    print(f"Found {len(group_images)} images containing faces from group {group_id}")
    
    # Set up output directory if specified
    if output_directory:
        os.makedirs(output_directory, exist_ok=True)
        print(f"Output directory created/verified: {output_directory}")
    
    # Prepare source directory
    source_directory = photographer_directory
    if not source_directory or not os.path.exists(source_directory):
        # Try to infer source directory from the first image path in the group
        if len(group_images) > 0:
            first_image = group_images[0]
            if os.path.dirname(first_image):
                source_directory = os.path.dirname(os.path.join(current_dir, first_image))
                print(f"Using inferred source directory: {source_directory}")
        
        if not source_directory or not os.path.exists(source_directory):
            print("Could not determine source directory for images")
            return []
    
    # Collect matching images with face locations
    matching_images = []
    
    for i, image_filename in enumerate(group_images):
        # Get full path of the original image
        if os.path.isabs(image_filename):
            # If it's already an absolute path, use it
            img_path = image_filename
        else:
            # Otherwise, join with the source directory
            img_path = os.path.join(source_directory, os.path.basename(image_filename))
        
        # Check if the file exists
        if not os.path.exists(img_path):
            print(f"Warning: Image file not found: {img_path}")
            continue
        
        # Find face locations in the image
        try:
            image = cv2.imread(img_path)
            if image is None:
                print(f"Could not read image: {img_path}")
                continue
                
            # Convert to RGB for face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            
            # Add to results
            matching_images.append((img_path, face_locations))
            print(f"[{i+1}/{len(group_images)}] Added image with {len(face_locations)} faces: {os.path.basename(img_path)}")
            
            # Copy to output directory if specified
            if output_directory:
                dest_path = os.path.join(output_directory, os.path.basename(img_path))
                shutil.copy2(img_path, dest_path)
                print(f"Copied to: {dest_path}")
        
        except Exception as e:
            print(f"Error processing image {img_path}: {e}")
    
    print(f"Successfully processed {len(matching_images)} out of {len(group_images)} images")
    return matching_images

def get_face_group_info(group_id):
    """Get information about a specific face group"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    groups_file = os.path.join(current_dir, "face_groups.json")
    labels_file = os.path.join(current_dir, "detected_faces", "face_labels.json")
    
    # Check if face groups data exists
    if not os.path.exists(groups_file):
        return {"error": f"Face groups data not found: {groups_file}"}
    
    # Load face groups data
    try:
        with open(groups_file, 'r') as f:
            groups_data = json.load(f)
    except Exception as e:
        return {"error": f"Error loading face groups data: {e}"}
    
    # Convert group_id to string if needed
    group_id = str(group_id)
    
    # Check if group exists
    if group_id not in groups_data:
        return {"error": f"Group ID {group_id} not found in face groups data"}
    
    # Get group data
    group_data = groups_data[group_id]
    
    # Try to get label from labels file
    label = ""
    if os.path.exists(labels_file):
        try:
            with open(labels_file, 'r') as f:
                labels_data = json.load(f)
                label = labels_data.get(group_id, "")
        except:
            pass
    
    # Create result
    result = {
        "group_id": group_id,
        "count": group_data.get("count", 0),
        "label": label or group_data.get("label", ""),
        "images": group_data.get("images", []),
    }
    
    return result

def select_face_images(group_id, photographer_directory, output_directory):
    """
    Select all images containing a specific face group and copy them to an output directory.
    This function is meant to be called after processor.py has completed face detection.
    
    Args:
        group_id: The ID of the face group
        photographer_directory: Path to the photographer's photos directory
        output_directory: Path to save copies of matching images
    
    Returns:
        Dictionary with the result of the operation
    """
    if not os.path.exists(photographer_directory):
        return {
            "status": "error", 
            "message": f"Photographer directory not found: {photographer_directory}"
        }
    
    # Create output directory
    os.makedirs(output_directory, exist_ok=True)
    
    # Get group info
    group_info = get_face_group_info(group_id)
    if "error" in group_info:
        return {"status": "error", "message": group_info["error"]}
    
    # Get matching images
    matching_images = get_matching_images_for_face(
        group_id, 
        photographer_directory=photographer_directory,
        output_directory=output_directory
    )
    
    if not matching_images:
        return {
            "status": "warning",
            "message": f"No matching images found for face group {group_id}"
        }
    
    # Create result
    result = {
        "status": "success",
        "message": f"Found {len(matching_images)} images with faces from group {group_id}",
        "group_info": group_info,
        "image_count": len(matching_images),
        "output_directory": output_directory
    }
    
    return result

def main():
    """Main function for command-line usage"""
    import argparse
    parser = argparse.ArgumentParser(description="Find images containing faces from a specific face group")
    parser.add_argument("group_id", type=int, help="ID of the face group to find")
    parser.add_argument("--photographer_dir", type=str, help="Path to photographer's photos directory")
    parser.add_argument("--output_dir", type=str, help="Path to save matching images")
    
    args = parser.parse_args()
    
    if not args.photographer_dir:
        # Try to get from environment or use default
        args.photographer_dir = os.environ.get("PHOTOGRAPHER_DIR", "")
    
    if not args.output_dir:
        # Create a temporary directory
        args.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                       f"matching_faces_group_{args.group_id}")
    
    result = select_face_images(args.group_id, args.photographer_dir, args.output_dir)
    
    if result["status"] == "success":
        print(f"Success: {result['message']}")
        print(f"Images saved to: {result['output_directory']}")
    else:
        print(f"Error: {result['message']}")
    
    return 0 if result["status"] == "success" else 1

if __name__ == "__main__":
    sys.exit(main())
