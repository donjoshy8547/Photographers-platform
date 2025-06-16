import os
import cv2
import face_recognition
import numpy as np
from collections import defaultdict
import json
import re
import random
import shutil
import sys

# Function to process images and detect repeated faces with high accuracy
def find_repeated_faces(image_folder, min_faces=3, tolerance=0.45, progress_callback=None):
    """
    Find faces that appear multiple times across different images in a folder.
    
    Args:
        image_folder: Path to folder containing images
        min_faces: Minimum number of occurrences to consider a face as repeated
        tolerance: Lower values make face matching more strict (0.0-1.0)
        progress_callback: Optional callback function to report progress
                          Function signature: callback(current_image, total_images, filename, faces_found)
    
    Returns:
        List of tuples (image_path, caption) for display in gallery
    """
    if not os.path.exists(image_folder):
        print(f"Image folder not found: {image_folder}")
        return []
    
    # Create output directory for cropped faces
    output_dir = os.path.join(os.path.dirname(__file__), "detected_faces")
    os.makedirs(output_dir, exist_ok=True)
    
    # Clear previous results
    print(f"Clearing previous detection results...")
    face_files_removed = 0
    for file in os.listdir(output_dir):
        if file.endswith('.jpg') and file.startswith('face_'):
            os.remove(os.path.join(output_dir, file))
            face_files_removed += 1
    print(f"Removed {face_files_removed} previous face images")
    
    # Store face encodings and their occurrences
    face_encodings = []
    face_data = []
    
    print(f"Processing images in {image_folder}...")
    
    # Get list of image files first to calculate total
    image_files = []
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(("png", "jpg", "jpeg", "webp")):
            image_files.append(filename)
    
    total_images = len(image_files)
    print(f"Found {total_images} images to process")
    
    # First pass: collect all face encodings
    for i, filename in enumerate(image_files):
        img_path = os.path.join(image_folder, filename)
        
        # Print progress
        print(f"Processing image {i+1}/{total_images}: {filename}")
        
        # Load the image
        image = cv2.imread(img_path)
        
        if image is None:
            print(f"  • Could not read {filename}, skipping...")
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(i+1, total_images, filename, [])
                
            continue
        
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find all face locations in the image
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            print(f"  • No faces found in {filename}")
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(i+1, total_images, filename, [])
                
            continue
        
        print(f"  • Found {len(face_locations)} faces in {filename}")
        
        # Get face encodings for all faces in the image
        batch_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        # Store face data
        for j, (encoding, location) in enumerate(zip(batch_encodings, face_locations)):
            top, right, bottom, left = location
            face_image = image[top:bottom, left:right]
            face_encodings.append(encoding)
            face_data.append({
                'encoding': encoding,
                'location': location,
                'image_path': img_path,
                'face_image': face_image,
                'index': j
            })
        
        # Call progress callback if provided
        if progress_callback:
            progress_callback(i+1, total_images, filename, face_locations)
    
    print(f"\nFound {len(face_encodings)} total faces across all images")
    print(f"Grouping similar faces (tolerance: {tolerance})...")
    
    # Group similar faces
    face_groups = defaultdict(list)
    group_id = 0
    
    for i, face in enumerate(face_data):
        # Check if this face matches any existing group
        matched = False
        
        for gid, members in face_groups.items():
            # Compare with the first face in the group (representative)
            if face_recognition.compare_faces([members[0]['encoding']], face['encoding'], tolerance=tolerance)[0]:
                face_groups[gid].append(face)
                matched = True
                break
        
        # If no match found, create a new group
        if not matched:
            face_groups[group_id].append(face)
            group_id += 1
    
    print(f"Identified {len(face_groups)} distinct face groups")
    
    # Filter groups that have at least min_faces occurrences
    filtered_groups = {gid: members for gid, members in face_groups.items() if len(members) >= min_faces}
    
    print(f"Found {len(filtered_groups)} face groups with at least {min_faces} occurrences")
    
    # Save the filtered groups to a JSON file for later use
    groups_data = {}
    for gid, members in filtered_groups.items():
        groups_data[str(gid)] = {
            'count': len(members),
            'images': [os.path.basename(member['image_path']) for member in members],
            'label': ''  # No label initially
        }
    
    with open(os.path.join(os.path.dirname(__file__), 'face_groups.json'), 'w') as f:
        json.dump(groups_data, f, indent=2)
    
    # Save representative faces from each group
    result_faces = []
    
    for gid, members in filtered_groups.items():
        # Use the first face as representative
        face = members[0]
        
        # Create a filename for the face
        face_filename = f"face_{gid}_group{len(members)}.jpg"
        face_path = os.path.join(output_dir, face_filename)
        
        # Save the face image
        cv2.imwrite(face_path, face['face_image'])
        
        # Create a caption
        caption = f"Group {gid}: ({len(members)} faces)"
        
        # Add to results
        result_faces.append((face_path, caption))
        print(f"Saved representative face for Group {gid} ({len(members)} occurrences)")
    
    print(f"\nFace detection complete. Found {len(result_faces)} face groups with at least {min_faces} occurrences.")
    
    return result_faces

def get_face_groups():
    """Get a list of face groups for the dropdown"""
    output_dir = os.path.join(os.path.dirname(__file__), "detected_faces")
    
    try:
        # Check if the directory exists
        if not os.path.exists(output_dir):
            print("Output directory does not exist")
            return []
        
        # Check if there are any face images
        face_files = [f for f in os.listdir(output_dir) if f.startswith("face_") and f.endswith(".jpg")]
        if not face_files:
            print("No face files found")
            return []
        
        # Extract unique group IDs
        group_ids = set()
        for filename in face_files:
            parts = filename.split("_")
            if len(parts) >= 3:
                group_ids.add(parts[1])
        
        # Load labels
        labels_file = os.path.join(output_dir, "face_labels.json")
        face_labels = {}
        if os.path.exists(labels_file):
            try:
                with open(labels_file, 'r') as f:
                    face_labels = json.load(f)
            except Exception as e:
                print(f"Error loading labels: {e}")
        
        # Create choices for dropdown
        choices = []
        for group_id in sorted(group_ids, key=int):
            group_num = int(group_id) + 1
            label = face_labels.get(group_id, "")
            if label:
                display = f"Group {group_num}: {label}"
            else:
                display = f"Group {group_num}"
            
            # Count instances
            count = len([f for f in face_files if f.startswith(f"face_{group_id}_")])
            display += f" ({count} faces)"
            
            choices.append(display)
        
        return choices
    except Exception as e:
        print(f"Error getting face groups: {e}")
        return []

def get_group_id_from_display(display_text):
    """Extract the group ID from the display text"""
    match = re.search(r"Group (\d+)", display_text)
    if match:
        group_num = int(match.group(1))
        return str(group_num - 1)
    return None

def label_face_group(group_display, label_text):
    """Label a face group with a name"""
    if not group_display:
        return "Please select a face group"
    
    if not label_text.strip():
        return "Please enter a label"
    
    group_id = get_group_id_from_display(group_display)
    if group_id is None:
        return "Could not determine group ID"
    
    output_dir = os.path.join(os.path.dirname(__file__), "detected_faces")
    labels_file = os.path.join(output_dir, "face_labels.json")
    
    # Load existing labels
    face_labels = {}
    if os.path.exists(labels_file):
        try:
            with open(labels_file, 'r') as f:
                face_labels = json.load(f)
        except:
            pass
    
    # Update label
    face_labels[group_id] = label_text.strip()
    
    # Save updated labels
    with open(labels_file, 'w') as f:
        json.dump(face_labels, f)
    
    # Update face groups info file if it exists
    groups_file = os.path.join(output_dir, "face_groups.json")
    if os.path.exists(groups_file):
        try:
            with open(groups_file, 'r') as f:
                groups_info = json.load(f)
                
            if group_id in groups_info:
                groups_info[group_id]["label"] = label_text.strip()
                
            with open(groups_file, 'w') as f:
                json.dump(groups_info, f)
        except:
            pass
    
    return f"Successfully labeled Group {int(group_id)+1} as '{label_text}'"

def delete_face_label(group_display):
    """Delete the label for a face group"""
    if not group_display:
        return "Please select a face group"
    
    group_id = get_group_id_from_display(group_display)
    if group_id is None:
        return "Could not determine group ID"
    
    output_dir = os.path.join(os.path.dirname(__file__), "detected_faces")
    labels_file = os.path.join(output_dir, "face_labels.json")
    
    # Load existing labels
    face_labels = {}
    if os.path.exists(labels_file):
        try:
            with open(labels_file, 'r') as f:
                face_labels = json.load(f)
        except:
            return "Could not load labels file"
    
    # Check if label exists
    if group_id not in face_labels:
        return f"Group {int(group_id)+1} does not have a label"
    
    # Remove label
    old_label = face_labels[group_id]
    del face_labels[group_id]
    
    # Save updated labels
    with open(labels_file, 'w') as f:
        json.dump(face_labels, f)
    
    # Update face groups info file if it exists
    groups_file = os.path.join(output_dir, "face_groups.json")
    if os.path.exists(groups_file):
        try:
            with open(groups_file, 'r') as f:
                groups_info = json.load(f)
                
            if group_id in groups_info:
                groups_info[group_id]["label"] = ""
                
            with open(groups_file, 'w') as f:
                json.dump(groups_info, f)
        except:
            pass
    
    return f"Successfully removed label '{old_label}' from Group {int(group_id)+1}"

def get_face_gallery():
    """Get all faces for the gallery"""
    output_dir = os.path.join(os.path.dirname(__file__), "detected_faces")
    
    if not os.path.exists(output_dir):
        return []
    
    # Find all face images
    face_images = []
    for filename in os.listdir(output_dir):
        if filename.startswith("face_") and filename.endswith(".jpg"):
            path = os.path.join(output_dir, filename)
            
            # Parse group and instance
            parts = filename.replace('.jpg', '').split('_')
            if len(parts) >= 3:
                group_id = int(parts[1])
                instance = int(parts[2])
                
                # Get label if available
                labels_file = os.path.join(output_dir, "face_labels.json")
                label = ""
                if os.path.exists(labels_file):
                    try:
                        with open(labels_file, 'r') as f:
                            face_labels = json.load(f)
                            label = face_labels.get(str(group_id), "")
                    except:
                        pass
                
                # Create caption
                caption = f"Group {group_id+1}"
                if label:
                    caption = f"{label} ({caption})"
                caption += f", Face {instance+1}"
                
                face_images.append((path, caption))
    
    return face_images

def show_group_faces(group_display):
    """Show all faces for a specific group"""
    if not group_display:
        return []
    
    group_id = get_group_id_from_display(group_display)
    if group_id is None:
        return []
    
    output_dir = os.path.join(os.path.dirname(__file__), "detected_faces")
    
    if not os.path.exists(output_dir):
        return []
    
    # Find all faces in the group
    group_faces = []
    for filename in os.listdir(output_dir):
        if filename.startswith(f"face_{group_id}_") and filename.endswith(".jpg"):
            path = os.path.join(output_dir, filename)
            
            # Parse instance
            parts = filename.replace('.jpg', '').split('_')
            if len(parts) >= 3:
                instance = int(parts[2])
                
                # Get label if available
                labels_file = os.path.join(output_dir, "face_labels.json")
                label = ""
                if os.path.exists(labels_file):
                    try:
                        with open(labels_file, 'r') as f:
                            face_labels = json.load(f)
                            label = face_labels.get(str(group_id), "")
                    except:
                        pass
                
                # Create caption
                caption = f"Group {int(group_id)+1}"
                if label:
                    caption = f"{label} ({caption})"
                caption += f", Face {instance+1}"
                
                group_faces.append((path, caption))
    
    # Sort by instance number
    group_faces.sort(key=lambda x: int(x[0].split('_')[-1].replace('.jpg', '')))
    
    return group_faces

def register_face(selected_face, face_name):
    """Register a selected face by copying it to the registered_faces folder"""
    if not selected_face or not os.path.exists(selected_face):
        return "No face selected or face not found"
    
    if not face_name or not face_name.strip():
        return "Please enter a valid name"
    
    # Sanitize the face name for filename
    sanitized_name = re.sub(r'[^\w\s]', '', face_name).strip()
    sanitized_name = sanitized_name.replace(' ', '_')
    
    # Create registered faces directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "registered_faces")
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Extract face information
        filename = os.path.basename(selected_face)
        parts = filename.replace('.jpg', '').split('_')
        
        if len(parts) >= 3 and parts[0] == "face":
            group_id = parts[1]
            instance = parts[2]
            
            # New filename format: name_groupid_instance.jpg
            new_filename = f"{sanitized_name}_{group_id}_{instance}.jpg"
            
            # Check if a face with this name already exists
            existing_faces = [f for f in os.listdir(output_dir) 
                             if f.startswith(f"{sanitized_name}_") and f.endswith(".jpg")]
            
            if existing_faces:
                # Add a number to avoid overwriting
                new_filename = f"{sanitized_name}_{len(existing_faces)+1}_{group_id}_{instance}.jpg"
            
            # Copy the face image to the registered faces directory
            shutil.copy2(selected_face, os.path.join(output_dir, new_filename))
            
            # Save registration info in JSON
            reg_file = os.path.join(output_dir, "registrations.json")
            registrations = {}
            
            if os.path.exists(reg_file):
                try:
                    with open(reg_file, 'r') as f:
                        registrations = json.load(f)
                except:
                    pass
            
            # Add or update registration
            if sanitized_name not in registrations:
                registrations[sanitized_name] = {"count": 1, "label": face_name}
            else:
                registrations[sanitized_name]["count"] += 1
            
            with open(reg_file, 'w') as f:
                json.dump(registrations, f)
            
            return f"Successfully registered face as '{face_name}'"
        else:
            return "Invalid face image format"
    except Exception as e:
        return f"Error registering face: {str(e)}"

def get_registered_faces():
    """Get all registered faces for the gallery"""
    output_dir = os.path.join(os.path.dirname(__file__), "registered_faces")
    
    if not os.path.exists(output_dir):
        return []
    
    # Find all registered face images
    face_images = []
    for filename in os.listdir(output_dir):
        if filename.endswith(".jpg"):
            path = os.path.join(output_dir, filename)
            
            # Try to extract name
            name_parts = filename.split("_")
            if len(name_parts) > 1:
                # First part is the name
                name = name_parts[0].replace("_", " ")
                caption = f"{name.title()}"
                face_images.append((path, caption))
    
    return face_images

def select_random_faces_from_groups(output_dir=None):
    """
    Select one random face from each face group and save to a new directory
    
    Args:
        output_dir: Directory to save the randomly selected faces
    
    Returns:
        Message with the result of the operation and list of selected faces
    """
    # Get the faces directory
    detected_faces_dir = os.path.join(os.path.dirname(__file__), "detected_faces")
    
    if not os.path.exists(detected_faces_dir):
        return "No detected faces found", []
    
    # If no output directory specified, create one
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(__file__), "random_selection")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Clear existing files
    for file in os.listdir(output_dir):
        if file.endswith('.jpg'):
            os.remove(os.path.join(output_dir, file))
    
    # Get all face groups
    groups = {}
    for filename in os.listdir(detected_faces_dir):
        if filename.startswith("face_") and filename.endswith(".jpg"):
            parts = filename.replace('.jpg', '').split('_')
            if len(parts) >= 3:
                group_id = parts[1]
                if group_id not in groups:
                    groups[group_id] = []
                groups[group_id].append(filename)
    
    if not groups:
        return "No face groups found", []
    
    # Load labels
    labels_file = os.path.join(detected_faces_dir, "face_labels.json")
    face_labels = {}
    if os.path.exists(labels_file):
        try:
            with open(labels_file, 'r') as f:
                face_labels = json.load(f)
        except:
            pass
    
    # Select one random face from each group
    selected_faces = []
    for group_id, faces in groups.items():
        if faces:
            random_face = random.choice(faces)
            src_path = os.path.join(detected_faces_dir, random_face)
            
            # Get group label if available
            label = face_labels.get(group_id, "")
            file_prefix = label.replace(" ", "_") if label else f"group_{group_id}"
            
            # Copy the face to the output directory
            dst_filename = f"{file_prefix}_{random_face}"
            dst_path = os.path.join(output_dir, dst_filename)
            shutil.copy2(src_path, dst_path)
            
            # Create caption
            group_num = int(group_id) + 1
            caption = f"Group {group_num}"
            if label:
                caption = f"{label} ({caption})"
            
            selected_faces.append((dst_path, caption))
    
    # Save metadata
    metadata = {
        "timestamp": None,
        "count": len(selected_faces),
        "groups": {k: {"label": face_labels.get(k, "")} for k in groups.keys()}
    }
    with open(os.path.join(output_dir, "selection_metadata.json"), 'w') as f:
        json.dump(metadata, f)
    
    message = f"Selected {len(selected_faces)} faces (one from each group)"
    return message, selected_faces

def get_random_selected_faces():
    """Get all randomly selected faces for the gallery"""
    output_dir = os.path.join(os.path.dirname(__file__), "random_selection")
    
    if not os.path.exists(output_dir):
        return []
    
    # Find all face images
    face_images = []
    for filename in os.listdir(output_dir):
        if filename.endswith(".jpg"):
            path = os.path.join(output_dir, filename)
            
            # Try to extract group info
            caption = "Selected face"
            if filename.startswith("group_"):
                parts = filename.split("_")
                if len(parts) >= 2:
                    group_id = parts[1]
                    caption = f"Group {int(group_id)+1}"
            elif "_face_" in filename:
                # Format is "label_face_group_instance.jpg"
                parts = filename.split("_face_")
                if len(parts) == 2:
                    label = parts[0].replace("_", " ")
                    caption = label
            
            face_images.append((path, caption))
    
    return face_images

def rename_selected_face(face_path, new_name):
    """
    Rename a selected face image with a user-provided name
    
    Args:
        face_path: Path to the selected face image
        new_name: New name to give the face image
    
    Returns:
        Message with the result of the operation
    """
    if not face_path or not os.path.exists(face_path):
        return "No face selected or face not found"
    
    if not new_name or not new_name.strip():
        return "Please enter a valid name"
    
    # Sanitize the new name (remove special characters)
    sanitized_name = re.sub(r'[^\w\s]', '', new_name).strip()
    sanitized_name = sanitized_name.replace(' ', '_')
    
    try:
        # Get directory and filename
        directory = os.path.dirname(face_path)
        filename = os.path.basename(face_path)
        
        # Build new filename, preserving original face info
        if "face_" in filename:
            # Format is "face_group_instance.jpg"
            face_info = filename[filename.find("face_"):]
            new_filename = f"{sanitized_name}_{face_info}"
        else:
            # Not a standard face file, just prepend the name
            new_filename = f"{sanitized_name}_{filename}"
        
        # Full path for new file
        new_path = os.path.join(directory, new_filename)
        
        # Rename the file
        shutil.move(face_path, new_path)
        
        return f"Successfully renamed face to '{new_name}'"
    
    except Exception as e:
        return f"Error renaming face: {str(e)}"

# Main execution point for command-line use
if __name__ == "__main__":
    import argparse
    
    # Create a command-line argument parser
    parser = argparse.ArgumentParser(description="Face Detection and Recognition Tool")
    parser.add_argument("--input", "-i", type=str, help="Path to the folder containing images", required=False)
    parser.add_argument("--min-faces", "-m", type=int, default=3, help="Minimum occurrences to consider a face as repeated (default: 3)")
    parser.add_argument("--tolerance", "-t", type=float, default=0.45, help="Matching tolerance - lower values are stricter (default: 0.45)")
    parser.add_argument("--random-select", "-r", action="store_true", help="Select one random face from each group")
    parser.add_argument("--list-groups", "-l", action="store_true", help="List all detected face groups")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("Face Detection Module")
        print("Use this module to detect and process faces in images.")
        print("\nExamples:")
        print("  Process images in a folder:")
        print("    python face.py --input /path/to/images")
        print("\n  Use stricter face matching (less false positives):")
        print("    python face.py --input /path/to/images --tolerance 0.4")
        print("\n  Require fewer occurrences to match a face:")
        print("    python face.py --input /path/to/images --min-faces 2")
        print("\n  Select one random face from each detected group:")
        print("    python face.py --random-select")
        print("\n  List all detected face groups:")
        print("    python face.py --list-groups")
        parser.print_help()
    else:
        # Process input folder if provided
        if args.input:
            print(f"Processing images in: {args.input}")
            results = find_repeated_faces(args.input, args.min_faces, args.tolerance)
            
            # Print results
            if results:
                print(f"\nFound {len(results)} faces in {args.input}")
                for i, (path, caption) in enumerate(results):
                    print(f"{i+1}. {os.path.basename(path)}: {caption}")
            else:
                print(f"No faces found in {args.input} that meet the criteria (min faces: {args.min_faces}, tolerance: {args.tolerance})")
                
            print(f"\nFaces saved to: {os.path.join(os.path.dirname(__file__), 'detected_faces')}")
        
        # List groups if requested
        if args.list_groups:
            groups = get_face_groups()
            if groups:
                print("\nFace Groups:")
                for i, group in enumerate(groups):
                    print(f"{i+1}. {group}")
            else:
                print("\nNo face groups found. Process images first.")
        
        # Select random faces if requested
        if args.random_select:
            message, selected = select_random_faces_from_groups()
            print(f"\n{message}")
            if selected:
                for i, (path, caption) in enumerate(selected):
                    print(f"{i+1}. {os.path.basename(path)}: {caption}")
                
                print(f"\nRandom faces saved to: {os.path.join(os.path.dirname(__file__), 'random_selection')}")
            else:
                print("No faces were selected. Process images first.")
