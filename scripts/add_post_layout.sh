#!/bin/bash

# Script to add layout: post to all markdown files in _posts that don't have a layout specified

POSTS_DIR="_posts"

echo "Adding layout: post to posts without a layout..."
echo ""

count=0

# Find all markdown files in _posts
find "$POSTS_DIR" -name "*.md" -type f | while read -r file; do
    # Check if file doesn't already have a layout specified
    if ! grep -q "^layout:" "$file"; then
        echo "Processing: $file"
        
        # Create a backup
        cp "$file" "$file.bak"
        
        # Find the line number of the closing --- of front matter
        # Then insert layout: post after the first ---
        # Using awk to insert after the first line (which should be ---)
        awk '
        NR == 1 && $0 == "---" {
            print $0
            print "layout: post"
            next
        }
        { print }
        ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        
        ((count++))
        echo "  ✓ Added layout: post"
    fi
done

echo ""
echo "Done! Added layout to $count files."
echo "Backup files (.bak) were created. Review changes and remove backups when satisfied."

