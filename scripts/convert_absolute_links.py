#!/usr/bin/env python3

"""
Convert absolute links to gobigemma.com/gobigemma.de posts to relative links.
Converts: http://www.gobigemma.com/2016/09/15/post-title/
To: /2016/09/15/post-title/ (or with baseurl: /gobigemma/2016/09/15/post-title/)
"""

import os
import re
import glob

POSTS_DIR = "_posts"
DOMAINS = ['www.gobigemma.com', 'gobigemma.com', 'gobigemma.de']

def convert_absolute_links(content):
    """Convert absolute gobigemma links to relative links."""
    updated = False
    new_content = content
    
    # Pattern to match markdown links: [text](http://www.gobigemma.com/path/)
    # or [text](http://gobigemma.de/path/)
    pattern = r'(\[([^\]]+)\]\(https?://(?:www\.)?gobigemma\.(?:com|de)([^\)]+)\))'
    
    def replace_link(match):
        full_match = match.group(1)
        link_text = match.group(2)
        path = match.group(3)
        
        # Remove trailing slash if present
        if path.endswith('/'):
            path = path[:-1]
        
        # Check if it's a post URL (format: /YYYY/MM/DD/title/)
        post_pattern = r'^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$'
        if re.match(post_pattern, path):
            # Convert to relative link
            # Since baseurl is "/gobigemma", we need to include it
            relative_path = f'/gobigemma{path}'
            return f'[{link_text}]({relative_path})'
        
        # For category/tag links, keep as is or convert appropriately
        # For now, just convert the domain part
        return f'[{link_text}]({path})'
    
    # Find all matches
    matches = list(re.finditer(pattern, new_content))
    if matches:
        # Replace from end to start to preserve positions
        for match in reversed(matches):
            replacement = replace_link(match)
            new_content = new_content[:match.start()] + replacement + new_content[match.end():]
            updated = True
    
    return new_content, updated

def main():
    print("Converting absolute links to relative links...")
    print("")
    
    post_files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    updated_count = 0
    total_replacements = 0
    
    for filepath in sorted(post_files):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content, updated = convert_absolute_links(content)
        
        if updated:
            # Count replacements
            old_links = len(re.findall(r'https?://(?:www\.)?gobigemma\.(?:com|de)', content))
            new_links = len(re.findall(r'https?://(?:www\.)?gobigemma\.(?:com|de)', new_content))
            replacements = old_links - new_links
            
            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            updated_count += 1
            total_replacements += replacements
            print(f"  ✓ {os.path.basename(filepath)} ({replacements} link(s) converted)")
    
    print("")
    print(f"Done! Updated {updated_count} files with {total_replacements} total link conversions.")

if __name__ == "__main__":
    main()

