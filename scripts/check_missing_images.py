#!/usr/bin/env python3

"""
Check all image references in posts and identify which images are missing from assets/images.
"""

import os
import re
import glob
from pathlib import Path

POSTS_DIR = "_posts"
ASSETS_IMAGES_DIR = "assets/images"

def get_all_images_in_assets():
    """Get a set of all image filenames in assets/images."""
    image_files = set()
    if os.path.exists(ASSETS_IMAGES_DIR):
        for file in os.listdir(ASSETS_IMAGES_DIR):
            if os.path.isfile(os.path.join(ASSETS_IMAGES_DIR, file)):
                image_files.add(file.lower())  # Use lowercase for case-insensitive comparison
    return image_files

def extract_image_references(content):
    """Extract all image references from markdown/HTML content."""
    images = set()
    
    # Pattern 1: Markdown image syntax ![alt](path)
    markdown_pattern = r'!\[[^\]]*\]\(([^\)]+)\)'
    matches = re.findall(markdown_pattern, content)
    for match in matches:
        # Remove query strings and fragments
        path = match.split('?')[0].split('#')[0]
        # Extract filename
        filename = os.path.basename(path)
        if filename:
            images.add(filename.lower())
    
    # Pattern 2: HTML img src="path"
    html_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    matches = re.findall(html_pattern, content)
    for match in matches:
        path = match.split('?')[0].split('#')[0]
        filename = os.path.basename(path)
        if filename:
            images.add(filename.lower())
    
    # Pattern 3: coverImage: "filename.jpg" in front matter
    cover_pattern = r'coverImage:\s*["\']([^"\']+)["\']'
    matches = re.findall(cover_pattern, content)
    for match in matches:
        filename = os.path.basename(match)
        if filename:
            images.add(filename.lower())
    
    # Pattern 4: Liquid template variables like {{ site.baseurl }}/assets/images/filename.jpg
    liquid_pattern = r'assets/images/([^"\'\s\)]+)'
    matches = re.findall(liquid_pattern, content)
    for match in matches:
        filename = os.path.basename(match)
        if filename:
            images.add(filename.lower())
    
    return images

def main():
    print("Checking for missing images...")
    print("")
    
    # Get all images in assets
    assets_images = get_all_images_in_assets()
    print(f"Images in {ASSETS_IMAGES_DIR}: {len(assets_images)}")
    
    # Get all image references from posts
    all_referenced_images = set()
    post_references = {}  # Track which post references which images
    
    post_files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    
    for filepath in sorted(post_files):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        referenced = extract_image_references(content)
        if referenced:
            post_name = os.path.basename(filepath)
            post_references[post_name] = referenced
            all_referenced_images.update(referenced)
    
    print(f"Unique images referenced in posts: {len(all_referenced_images)}")
    print("")
    
    # Find missing images
    missing_images = []
    for img_ref in sorted(all_referenced_images):
        if img_ref not in assets_images:
            # Find which posts reference this image
            posts_with_image = [post for post, imgs in post_references.items() if img_ref in imgs]
            missing_images.append((img_ref, posts_with_image))
    
    if missing_images:
        print(f"Missing images: {len(missing_images)}")
        print("=" * 80)
        print()
        
        for img_name, posts in sorted(missing_images):
            print(f"❌ {img_name}")
            print(f"   Referenced in: {', '.join(posts)}")
            print()
        
        # Write to file
        output_file = "missing_images.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Missing Images Report\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total missing images: {len(missing_images)}\n\n")
            for img_name, posts in sorted(missing_images):
                f.write(f"{img_name}\n")
                f.write(f"  Referenced in: {', '.join(posts)}\n\n")
        
        print(f"Report saved to: {output_file}")
    else:
        print("✓ All referenced images exist in assets/images!")
    
    print("")
    print(f"Summary:")
    print(f"  - Images in assets: {len(assets_images)}")
    print(f"  - Images referenced: {len(all_referenced_images)}")
    print(f"  - Missing images: {len(missing_images)}")

if __name__ == "__main__":
    main()

