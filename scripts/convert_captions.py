#!/usr/bin/env python3

"""
Convert WordPress caption shortcodes to HTML figure tags.
Converts: [caption ...]![alt](img.jpg) Caption text[/caption]
To: <figure><img src="..." alt="..."><figcaption>Caption text</figcaption></figure>
"""

import os
import re
import glob

POSTS_DIR = "_posts"

def convert_caption(match):
    """Convert a WordPress caption shortcode to HTML figure tag."""
    full_match = match.group(0)
    
    # Extract the image markdown syntax
    img_match = re.search(r'!\[([^\]]*)\]\(([^\)]+)\)', full_match)
    if not img_match:
        return full_match  # Return unchanged if no image found
    
    alt_text = img_match.group(1)
    img_src = img_match.group(2)
    
    # Extract caption text (everything after the image markdown, before [/caption])
    caption_match = re.search(r'\)\s+(.+?)\[/caption\]', full_match, re.DOTALL)
    if not caption_match:
        return full_match  # Return unchanged if no caption found
    
    caption_text = caption_match.group(1).strip()
    
    # Extract alignment if present
    align_match = re.search(r'align="([^"]+)"', full_match)
    align_class = ''
    if align_match:
        align = align_match.group(1)
        if align == 'aligncenter':
            align_class = ' class="align-center"'
        elif align == 'alignright':
            align_class = ' class="align-right"'
        elif align == 'alignleft':
            align_class = ' class="align-left"'
    
    # Build HTML figure tag
    figure_html = f'<figure{align_class}>\n  <img src="{img_src}" alt="{alt_text}">\n  <figcaption>{caption_text}</figcaption>\n</figure>'
    
    return figure_html

def process_file(filepath):
    """Process a single markdown file to convert captions."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match WordPress caption shortcodes (with escaped brackets)
    # Matches: \[caption ...\]![alt](img.jpg) Caption text\[/caption\]
    pattern = r'\\\[caption[^\]]*\\\].*?\\\[/caption\\\]'
    
    # Find all matches
    matches = list(re.finditer(pattern, content, re.DOTALL))
    if not matches:
        return False
    
    # Replace from end to start to preserve positions
    for match in reversed(matches):
        replacement = convert_caption_escaped(match)
        content = content[:match.start()] + replacement + content[match.end():]
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def convert_caption_escaped(match):
    """Convert an escaped WordPress caption shortcode to HTML figure tag."""
    full_match = match.group(0)
    
    # Remove escape backslashes for processing
    unescaped = full_match.replace('\\[', '[').replace('\\]', ']')
    
    # Extract the image markdown syntax
    img_match = re.search(r'!\[([^\]]*)\]\(([^\)]+)\)', unescaped)
    if not img_match:
        return full_match  # Return unchanged if no image found
    
    alt_text = img_match.group(1)
    img_src = img_match.group(2)
    
    # Extract caption text (everything after the image markdown, before [/caption])
    caption_match = re.search(r'\)\s+(.+?)\[/caption\]', unescaped, re.DOTALL)
    if not caption_match:
        return full_match  # Return unchanged if no caption found
    
    caption_text = caption_match.group(1).strip()
    
    # Extract alignment if present
    align_match = re.search(r'align="([^"]+)"', unescaped)
    align_class = ''
    if align_match:
        align = align_match.group(1)
        if align == 'aligncenter':
            align_class = ' class="align-center"'
        elif align == 'alignright':
            align_class = ' class="align-right"'
        elif align == 'alignleft':
            align_class = ' class="align-left"'
    
    # Build HTML figure tag
    figure_html = f'<figure{align_class}>\n  <img src="{img_src}" alt="{alt_text}">\n  <figcaption>{caption_text}</figcaption>\n</figure>'
    
    return figure_html

def main():
    print("Converting WordPress captions to HTML figure tags...")
    print("")
    
    count = 0
    post_files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    
    for filepath in sorted(post_files):
        if process_file(filepath):
            print(f"  ✓ Converted captions in {os.path.basename(filepath)}")
            count += 1
    
    print("")
    print(f"Done! Converted captions in {count} files.")

if __name__ == "__main__":
    main()

