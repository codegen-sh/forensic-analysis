#!/bin/bash

# Image optimization script for forensic analysis site
# Converts PNG images to WebP format while maintaining forensic quality

echo "🔄 Starting image optimization..."

# Create optimized directories
for splice_dir in docs/splice_frames/splice_*; do
    if [ -d "$splice_dir" ]; then
        echo "Processing $splice_dir..."
        
        # Convert PNG to WebP with high quality (90) to maintain forensic integrity
        for png_file in "$splice_dir"/*.png; do
            if [ -f "$png_file" ]; then
                webp_file="${png_file%.png}.webp"
                echo "  Converting $(basename "$png_file") to WebP..."
                
                # Use quality 90 to maintain forensic detail while reducing size
                cwebp -q 90 -m 6 -mt "$png_file" -o "$webp_file"
                
                # Check if conversion was successful
                if [ $? -eq 0 ]; then
                    original_size=$(stat -f%z "$png_file" 2>/dev/null || stat -c%s "$png_file")
                    webp_size=$(stat -f%z "$webp_file" 2>/dev/null || stat -c%s "$webp_file")
                    reduction=$((100 - (webp_size * 100 / original_size)))
                    echo "    ✅ Reduced by ${reduction}% ($(numfmt --to=iec $original_size) → $(numfmt --to=iec $webp_size))"
                else
                    echo "    ❌ Failed to convert $png_file"
                fi
            fi
        done
    fi
done

echo "📊 Calculating total savings..."
original_total=$(find docs/splice_frames -name "*.png" -exec stat -f%z {} + 2>/dev/null || find docs/splice_frames -name "*.png" -exec stat -c%s {} + | paste -sd+ | bc)
webp_total=$(find docs/splice_frames -name "*.webp" -exec stat -f%z {} + 2>/dev/null || find docs/splice_frames -name "*.webp" -exec stat -c%s {} + | paste -sd+ | bc)

if [ -n "$original_total" ] && [ -n "$webp_total" ]; then
    total_reduction=$((100 - (webp_total * 100 / original_total)))
    echo "🎉 Total size reduction: ${total_reduction}%"
    echo "   Original: $(numfmt --to=iec $original_total)"
    echo "   WebP: $(numfmt --to=iec $webp_total)"
    echo "   Saved: $(numfmt --to=iec $((original_total - webp_total)))"
fi

echo "✅ Image optimization complete!"

