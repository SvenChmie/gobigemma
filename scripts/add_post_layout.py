#!/usr/bin/env python3

import os
import re
import glob

POSTS_DIR = "_posts"

def add_layout_to_post(filepath):
    """Add layout: post to a post file if it doesn't have a layout."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if layout is already specified
    if re.search(r'^layout:', content, re.MULTILINE):
        return False
    
    # Check if file starts with front matter
    if not content.startswith('---'):
        return False
    
    # Find the end of front matter (second ---)
    lines = content.split('\n')
    if lines[0] != '---':
        return False
    
    # Find where front matter ends
    front_matter_end = None
    for i in range(1, len(lines)):
        if lines[i] == '---':
            front_matter_end = i
            break
    
    if front_matter_end is None:
        return False
    
    # Insert layout: post right after the opening ---
    new_lines = lines[:1] + ['layout: post'] + lines[1:]
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    return True

def main():
    print("Adding layout: post to posts without a layout...")
    print("")
    
    count = 0
    post_files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    
    for filepath in sorted(post_files):
        if add_layout_to_post(filepath):
            print(f"  ✓ Added layout: post to {os.path.basename(filepath)}")
            count += 1
    
    print("")
    print(f"Done! Added layout to {count} files.")

if __name__ == "__main__":
    main()

