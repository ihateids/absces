"""
Center a cropped image on a blank portrait canvas matching the size of reference images.
Creates both full-size and thumbnail versions.

Usage: python center_image_batch.py <image_filename>
Example: python center_image_batch.py 20251120_200309.jpg
"""

from PIL import Image
import os
import sys

# Paths - Update these if your folder structure is different
PHOTOS_DIR = r"c:\_vanda\otherdata\absces\photos\ori"
THUMBNAIL_DIR = r"c:\_vanda\otherdata\absces\photos"

def get_portrait_canvas_size():
    """
    Analyze all images and return the standard portrait canvas size.
    Always returns portrait orientation (height > width).
    """
    sizes = {}
    
    # Scan all images except already centered ones
    for filename in os.listdir(PHOTOS_DIR):
        if filename.endswith(('.jpg', '.jpeg', '.png')) and not filename.endswith('_centered.jpg'):
            try:
                img_path = os.path.join(PHOTOS_DIR, filename)
                with Image.open(img_path) as img:
                    size = img.size
                    sizes[size] = sizes.get(size, 0) + 1
            except Exception:
                pass
    
    if not sizes:
        print("Error: No reference images found")
        return None
    
    # Get most common size
    most_common = max(sizes.items(), key=lambda x: x[1])[0]
    
    # Convert to portrait orientation (height > width)
    if most_common[0] > most_common[1]:
        most_common = (most_common[1], most_common[0])
    
    print(f"Canvas size: {most_common[0]}x{most_common[1]} (Portrait)")
    return most_common

def center_image_on_canvas(target_filename, canvas_size):
    """
    Center the target image on a white canvas and create both full-size and thumbnail.
    Returns the output filename if successful, None otherwise.
    """
    target_path = os.path.join(PHOTOS_DIR, target_filename)
    
    if not os.path.exists(target_path):
        print(f"Error: Image not found: {target_path}")
        return None
    
    # Generate output filename
    name_without_ext = os.path.splitext(target_filename)[0]
    output_filename = f"{name_without_ext}_centered.jpg"
    output_path = os.path.join(PHOTOS_DIR, output_filename)
    thumbnail_path = os.path.join(THUMBNAIL_DIR, output_filename)
    
    # Process the image
    with Image.open(target_path) as target_img:
        target_width, target_height = target_img.size
        canvas_width, canvas_height = canvas_size
        
        print(f"Target image: {target_width}x{target_height}")
        
        # Create white canvas
        canvas = Image.new('RGB', canvas_size, (255, 255, 255))
        
        # Calculate center position
        x_offset = (canvas_width - target_width) // 2
        y_offset = (canvas_height - target_height) // 2
        
        print(f"Centering at: ({x_offset}, {y_offset})")
        
        # Paste target image onto canvas
        canvas.paste(target_img, (x_offset, y_offset))
        
        # Save full-size version
        canvas.save(output_path, quality=95)
        print(f"✓ Saved: {output_filename}")
        
        # Create thumbnail
        canvas.thumbnail((800, 800), Image.Resampling.LANCZOS)
        canvas.save(thumbnail_path, quality=85, optimize=True)
        print(f"✓ Thumbnail created")
        
    return output_filename

def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("Center Image on Canvas")
        print("=" * 60)
        print("\nUsage: python center_image_batch.py <image_filename>")
        print("Example: python center_image_batch.py 20251120_200309.jpg")
        print("\nThis script:")
        print("  - Centers a cropped image on a portrait canvas")
        print("  - Matches the size of other images in the folder")
        print("  - Creates both full-size and thumbnail versions")
        print("=" * 60)
        sys.exit(1)
    
    target_filename = sys.argv[1]
    
    print("\n" + "=" * 60)
    print(f"Processing: {target_filename}")
    print("=" * 60)
    
    # Get canvas size
    canvas_size = get_portrait_canvas_size()
    if not canvas_size:
        sys.exit(1)
    
    # Center the image
    output_filename = center_image_on_canvas(target_filename, canvas_size)
    
    if output_filename:
        print("\n" + "=" * 60)
        print("✓ Success!")
        print("=" * 60)
        print(f"\nCreated: {output_filename}")
        print(f"\nTo update gallery.html, replace:")
        print(f'  "{target_filename}"')
        print(f"with:")
        print(f'  "{output_filename}"')
        print("=" * 60 + "\n")
    else:
        print("\n✗ Failed to process image\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
