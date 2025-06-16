# Face detection module initialization
# This module provides functionality for detecting and grouping faces in images

# Import all functions from the face.py module to make them available
from .face import (
    find_repeated_faces,
    get_face_groups,
    label_face_group,
    select_random_faces_from_groups,
    get_random_selected_faces
)
