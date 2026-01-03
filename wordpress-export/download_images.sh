#!/bin/bash

# Script to download all images from the WordPress XML export
# Usage: ./download_images.sh

# Configuration
URLS_FILE="image_urls_list.txt"
DOWNLOAD_DIR="downloaded_images"
LOG_FILE="download_log.txt"
ERROR_LOG="download_errors.txt"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create download directory
mkdir -p "$DOWNLOAD_DIR"

# Initialize counters
total=$(wc -l < "$URLS_FILE" | tr -d ' ')
downloaded=0
skipped=0
failed=0

echo "Starting download of $total images..."
echo "Download directory: $DOWNLOAD_DIR"
echo ""

# Clear previous logs
> "$LOG_FILE"
> "$ERROR_LOG"

# Read URLs and download
while IFS= read -r url; do
    # Extract filename and path from URL
    # Remove protocol and domain, keep the path
    path=$(echo "$url" | sed -E 's|https?://[^/]+||')
    
    # Create full local path
    local_path="$DOWNLOAD_DIR$path"
    local_dir=$(dirname "$local_path")
    
    # Create directory if it doesn't exist
    mkdir -p "$local_dir"
    
    # Check if file already exists
    if [ -f "$local_path" ]; then
        echo -e "${YELLOW}[SKIP]${NC} Already exists: $(basename "$local_path")"
        ((skipped++))
        continue
    fi
    
    # Download the file
    if curl -L -f -s -S --max-time 30 --retry 2 -o "$local_path" "$url"; then
        echo -e "${GREEN}[OK]${NC} Downloaded: $(basename "$local_path")"
        echo "$url -> $local_path" >> "$LOG_FILE"
        ((downloaded++))
    else
        echo -e "${RED}[FAIL]${NC} Failed: $url"
        echo "$url" >> "$ERROR_LOG"
        # Remove empty file if download failed
        [ -f "$local_path" ] && rm "$local_path"
        ((failed++))
    fi
    
    # Show progress every 10 files
    total_processed=$((downloaded + skipped + failed))
    if [ $((total_processed % 10)) -eq 0 ]; then
        echo "Progress: $total_processed/$total (Downloaded: $downloaded, Skipped: $skipped, Failed: $failed)"
    fi
    
done < "$URLS_FILE"

# Final summary
echo ""
echo "=========================================="
echo "Download Complete!"
echo "=========================================="
echo "Total URLs: $total"
echo -e "${GREEN}Successfully downloaded: $downloaded${NC}"
echo -e "${YELLOW}Skipped (already exists): $skipped${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo ""
echo "Downloaded files are in: $DOWNLOAD_DIR"
echo "Success log: $LOG_FILE"
if [ $failed -gt 0 ]; then
    echo "Error log: $ERROR_LOG"
fi

