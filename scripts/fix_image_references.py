#!/usr/bin/env python3

"""
Find missing image references and update them to use existing originals.
Handles:
- Resized versions (e.g., image-300x200.jpg -> image.jpg)
- Case differences
- Different naming patterns
"""

import os
import re
import glob
from pathlib import Path

POSTS_DIR = "_posts"
ASSETS_IMAGES_DIR = "assets/images"

def get_all_images_in_assets():
    """Get a dictionary of all image filenames in assets/images (case-insensitive)."""
    image_files = {}
    if os.path.exists(ASSETS_IMAGES_DIR):
        for file in os.listdir(ASSETS_IMAGES_DIR):
            if os.path.isfile(os.path.join(ASSETS_IMAGES_DIR, file)):
                # Store both lowercase and original case
                image_files[file.lower()] = file
    return image_files

def find_original_image(missing_filename, assets_images):
    """
    Try to find the original version of a missing image.
    Returns the actual filename (with correct case) if found, None otherwise.
    """
    missing_lower = missing_filename.lower()
    
    # Strategy 1: Check if exact match exists (case-insensitive)
    if missing_lower in assets_images:
        return assets_images[missing_lower]
    
    # Strategy 2: Remove dimension suffixes (e.g., -300x200, -1024x683)
    # Pattern: filename-123x456.jpg -> filename.jpg
    base_pattern = re.sub(r'-\d+x\d+\.(jpg|jpeg|png|gif)$', r'.\1', missing_lower, flags=re.IGNORECASE)
    if base_pattern != missing_lower and base_pattern in assets_images:
        return assets_images[base_pattern]
    
    # Strategy 3: Remove dimension with underscore
    base_pattern2 = re.sub(r'_\d+x\d+\.(jpg|jpeg|png|gif)$', r'.\1', missing_lower, flags=re.IGNORECASE)
    if base_pattern2 != missing_lower and base_pattern2 in assets_images:
        return assets_images[base_pattern2]
    
    # Strategy 4: Remove common WordPress suffixes like -scaled, -resized
    base_pattern3 = re.sub(r'-(scaled|resized)-\d+x\d+\.(jpg|jpeg|png|gif)$', r'.\2', missing_lower, flags=re.IGNORECASE)
    if base_pattern3 != missing_lower and base_pattern3 in assets_images:
        return assets_images[base_pattern3]
    
    base_pattern4 = re.sub(r'-(scaled|resized)\.(jpg|jpeg|png|gif)$', r'.\2', missing_lower, flags=re.IGNORECASE)
    if base_pattern4 != missing_lower and base_pattern4 in assets_images:
        return assets_images[base_pattern4]
    
    # Strategy 5: Try removing just the dimension part before extension
    # e.g., image-e1465505996552-1024x404.jpg -> image-e1465505996552.jpg
    base_pattern5 = re.sub(r'-\d+x\d+\.(jpg|jpeg|png|gif)$', r'.\1', missing_lower, flags=re.IGNORECASE)
    if base_pattern5 != missing_lower:
        # Try variations
        variations = [
            base_pattern5,
            base_pattern5.replace('_', '-'),
            base_pattern5.replace('-', '_'),
        ]
        for var in variations:
            if var in assets_images:
                return assets_images[var]
    
    # Strategy 6: Try case variations of the base name
    # Get base name without extension
    base_name = os.path.splitext(missing_lower)[0]
    ext = os.path.splitext(missing_lower)[1]
    
    # Try common case variations
    for key, value in assets_images.items():
        if key.startswith(base_name.split('-')[0]) and key.endswith(ext):
            # Check if it's likely the same image
            if abs(len(key) - len(missing_lower)) < 20:  # Reasonable length difference
                return value
    
    return None

def update_image_reference(content, old_filename, new_filename):
    """Update all references to old_filename with new_filename in content (case-insensitive)."""
    updated = False
    new_content = content
    old_lower = old_filename.lower()
    
    # Pattern 1: Markdown image syntax ![alt](path/filename) - case insensitive
    pattern1 = r'(\!\[[^\]]*\]\([^\)]*/)([^/\)]+)([^\)]*\))'
    def repl1(match):
        path_part = match.group(1)
        filename_part = match.group(2)
        rest = match.group(3)
        if filename_part.lower() == old_lower:
            return path_part + new_filename + rest
        return match.group(0)
    if old_lower in new_content.lower():
        new_content = re.sub(pattern1, repl1, new_content, flags=re.IGNORECASE)
        if new_content != content:
            updated = True
    
    # Pattern 2: HTML img src="path/filename" - case insensitive
    pattern2 = r'(<img[^>]+src=["\']([^"\']*)/)([^/"\']+)([^"\']*["\'])'
    def repl2(match):
        path_part = match.group(1)
        filename_part = match.group(3)
        rest = match.group(4)
        if filename_part.lower() == old_lower:
            return path_part + new_filename + rest
        return match.group(0)
    if old_lower in new_content.lower():
        new_content = re.sub(pattern2, repl2, new_content, flags=re.IGNORECASE)
        if new_content != content:
            updated = True
    
    # Pattern 3: Liquid template {{ site.baseurl }}/assets/images/filename - case insensitive
    pattern3 = r'(assets/images/)([^"\'\s\)]+)'
    def repl3(match):
        path_part = match.group(1)
        filename_part = match.group(2)
        if filename_part.lower() == old_lower:
            return path_part + new_filename
        return match.group(0)
    if old_lower in new_content.lower():
        new_content = re.sub(pattern3, repl3, new_content, flags=re.IGNORECASE)
        if new_content != content:
            updated = True
    
    # Pattern 4: In figure tags <figure><img src="...filename...">
    pattern4 = r'(<figure[^>]*>.*?<img[^>]+src=["\']([^"\']*)/)([^/"\']+)([^"\']*["\'].*?</figure>)'
    def repl4(match):
        path_part = match.group(1)
        filename_part = match.group(3)
        rest = match.group(4)
        if filename_part.lower() == old_lower:
            return path_part + new_filename + rest
        return match.group(0)
    if old_lower in new_content.lower():
        new_content = re.sub(pattern4, repl4, new_content, flags=re.IGNORECASE | re.DOTALL)
        if new_content != content:
            updated = True
    
    return new_content, updated

def main():
    print("Finding and fixing image references...")
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
        
        # Extract image references
        images = set()
        
        # Markdown images
        markdown_pattern = r'!\[[^\]]*\]\(([^\)]+)\)'
        for match in re.findall(markdown_pattern, content):
            path = match.split('?')[0].split('#')[0]
            filename = os.path.basename(path)
            if filename:
                images.add(filename.lower())
        
        # HTML img tags
        html_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        for match in re.findall(html_pattern, content):
            path = match.split('?')[0].split('#')[0]
            filename = os.path.basename(path)
            if filename:
                images.add(filename.lower())
        
        # Liquid templates
        liquid_pattern = r'assets/images/([^"\'\s\)]+)'
        for match in re.findall(liquid_pattern, content):
            filename = os.path.basename(match)
            if filename:
                images.add(filename.lower())
        
        if images:
            post_name = os.path.basename(filepath)
            post_references[post_name] = (images, filepath, content)
            all_referenced_images.update(images)
    
    print(f"Unique images referenced in posts: {len(all_referenced_images)}")
    print("")
    
    # Find missing images and their replacements
    fixes = []
    for img_ref in sorted(all_referenced_images):
        if img_ref not in assets_images:
            original = find_original_image(img_ref, assets_images)
            if original:
                fixes.append((img_ref, original))
    
    if not fixes:
        print("No fixable image references found.")
        return
    
    print(f"Found {len(fixes)} fixable image references:")
    for old, new in fixes:
        print(f"  {old} -> {new}")
    print("")
    
    # Update posts
    updated_posts = []
    total_replacements = 0
    
    for post_name, (images, filepath, content) in post_references.items():
        new_content = content
        post_updated = False
        post_replacements = 0
        
        for old_img, new_img in fixes:
            if old_img in images:
                # Need to find the actual case used in the file
                # Try to find the exact reference
                old_content = new_content
                new_content, updated = update_image_reference(new_content, old_img, new_img)
                if updated:
                    post_updated = True
                    post_replacements += new_content.count(new_img) - old_content.count(new_img)
        
        if post_updated:
            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            updated_posts.append((post_name, post_replacements))
            total_replacements += post_replacements
    
    print("=" * 80)
    print(f"Updated {len(updated_posts)} posts:")
    for post_name, count in updated_posts:
        print(f"  ✓ {post_name} ({count} replacement(s))")
    print("")
    print(f"Total replacements: {total_replacements}")

if __name__ == "__main__":
    main()

