#!/bin/bash

# Script to fix image paths in Jekyll markdown files
# Changes relative paths like "images/filename.jpg" to "{{ site.baseurl }}/assets/images/filename.jpg"

POSTS_DIR="_posts"

echo "Fixing image paths in markdown files..."
echo ""

count=0

# Find all markdown files and fix image references
find "$POSTS_DIR" -name "*.md" -type f | while read -r file; do
    # Check if file contains image references
    if grep -q "images/" "$file"; then
        echo "Processing: $file"
        
        # Create a backup
        cp "$file" "$file.bak"
        
        # Replace image paths in markdown syntax: ![alt](images/...) -> ![alt]({{ site.baseurl }}/assets/images/...)
        sed -i '' 's|(images/|({{ site.baseurl }}/assets/images/|g' "$file"
        
        # Replace image paths in HTML img tags: <img src="images/... -> <img src="{{ site.baseurl }}/assets/images/...
        sed -i '' 's|<img src="images/|<img src="{{ site.baseurl }}/assets/images/|g' "$file"
        
        # Replace image paths in HTML img tags with single quotes
        sed -i '' "s|<img src='images/|<img src='{{ site.baseurl }}/assets/images/|g" "$file"
        
        # Remove backup if no changes were made (compare files)
        if cmp -s "$file" "$file.bak"; then
            rm "$file.bak"
        else
            ((count++))
            echo "  ✓ Fixed image paths"
        fi
    fi
done

echo ""
echo "Done! Fixed $count files."
echo "Backup files (.bak) were created. Review changes and remove backups when satisfied."

