#!/usr/bin/env python3

"""
Compare images in assets/images and wordpress-export/downloaded_images.
Copy files from downloaded_images that don't exist in assets/images.
"""

import os
import shutil
from pathlib import Path

ASSETS_IMAGES_DIR = "assets/images"
DOWNLOADED_IMAGES_DIR = "wordpress-export/downloaded_images"

def get_image_files(directory):
    """Get all image files from a directory (recursively)."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.ico'}
    image_files = {}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            if ext in image_extensions:
                # Use just the filename as the key (not the full path)
                filename = file_path.name
                full_path = str(file_path)
                image_files[filename] = full_path
    
    return image_files

def main():
    print("Comparing image directories...")
    print("")
    
    # Get all images from both directories
    assets_images = get_image_files(ASSETS_IMAGES_DIR)
    downloaded_images = get_image_files(DOWNLOADED_IMAGES_DIR)
    
    print(f"Images in {ASSETS_IMAGES_DIR}: {len(assets_images)}")
    print(f"Images in {DOWNLOADED_IMAGES_DIR}: {len(downloaded_images)}")
    print("")
    
    # Find images that exist in downloaded_images but not in assets/images
    missing_images = {}
    for filename, source_path in downloaded_images.items():
        if filename not in assets_images:
            missing_images[filename] = source_path
    
    print(f"Images to copy: {len(missing_images)}")
    print("")
    
    if not missing_images:
        print("No missing images found. All images are already in assets/images.")
        return
    
    # Copy missing images
    copied_count = 0
    skipped_count = 0
    
    for filename, source_path in sorted(missing_images.items()):
        dest_path = os.path.join(ASSETS_IMAGES_DIR, filename)
        
        # Check if destination already exists (shouldn't happen, but just in case)
        if os.path.exists(dest_path):
            print(f"  ⚠ Skipping {filename} (already exists)")
            skipped_count += 1
            continue
        
        try:
            shutil.copy2(source_path, dest_path)
            print(f"  ✓ Copied {filename}")
            copied_count += 1
        except Exception as e:
            print(f"  ✗ Error copying {filename}: {e}")
    
    print("")
    print(f"Done! Copied {copied_count} files, skipped {skipped_count} files.")

if __name__ == "__main__":
    main()

