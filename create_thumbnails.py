#!/usr/bin/env python3
"""
Complete Image Processing and Thumbnail Management Script

This is the main script for all image processing tasks:
- Creates thumbnails at 20% of original image size
- Checks existing thumbnails and recreates them if they're not the correct size
- Automatically rotates landscape images with width 4000 to portrait orientation
- Applies white patch auto white balance to new images for color correction
- Applies auto levels adjustment to new images for optimal contrast
- Preserves existing processed images (only processes new additions)

Usage: python create_thumbnails.py

This script replaces all individual processing scripts and provides comprehensive
image enhancement for any new images added to the photos folder.
"""

import os
from PIL import Image
import sys
import numpy as np

def get_image_size(image_path):
    """Get image dimensions"""
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None

def needs_rotation(img):
    """Check if image needs rotation (landscape with width 4000)"""
    width, height = img.size
    return width == 4000 and width > height

def apply_white_patch_white_balance(image):
    """
    Apply White Patch auto white balance to PIL image
    Assumes the brightest point in the image should be pure white
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    img_array = np.array(image).astype(np.float64)
    
    # Find maximum values in each channel
    max_r = np.max(img_array[:, :, 0])
    max_g = np.max(img_array[:, :, 1])
    max_b = np.max(img_array[:, :, 2])
    
    # Calculate scaling factors to make max values = 255
    scale_r = 255.0 / max_r if max_r > 0 else 1
    scale_g = 255.0 / max_g if max_g > 0 else 1
    scale_b = 255.0 / max_b if max_b > 0 else 1
    
    # Apply scaling
    balanced = img_array.copy()
    balanced[:, :, 0] *= scale_r
    balanced[:, :, 1] *= scale_g
    balanced[:, :, 2] *= scale_b
    
    # Clip values to 0-255 range and convert back to PIL image
    balanced = np.clip(balanced, 0, 255)
    return Image.fromarray(np.uint8(balanced))

def apply_auto_levels(image):
    """
    Apply auto levels adjustment to PIL image
    Stretches the histogram to use the full 0-255 range for each color channel
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    img_array = np.array(image).astype(np.float64)
    
    adjusted = img_array.copy()
    
    for channel in range(3):
        channel_data = img_array[:, :, channel]
        min_val = np.min(channel_data)
        max_val = np.max(channel_data)
        
        if max_val > min_val:
            # Stretch to 0-255 range
            adjusted[:, :, channel] = (channel_data - min_val) * 255.0 / (max_val - min_val)
        # If min_val == max_val, the channel is uniform, so no adjustment needed
    
    # Clip values to 0-255 range and convert back to PIL image
    adjusted = np.clip(adjusted, 0, 255)
    return Image.fromarray(np.uint8(adjusted))

def create_thumbnail(input_path, output_path, scale_factor=0.2, apply_white_balance=False):
    """Create thumbnail at specified scale factor (default 20%), rotating and optionally white balancing"""
    try:
        with Image.open(input_path) as img:
            original_processing_done = False
            
            # Convert to RGB if needed for consistent processing
            if img.mode != 'RGB':
                img = img.convert('RGB')
                print(f"  📷 Converted {os.path.basename(input_path)} to RGB mode")
            
            # Check if image needs rotation
            if needs_rotation(img):
                print(f"  📸 Rotating landscape image {os.path.basename(input_path)} to portrait...")
                # Rotate image clockwise by 90 degrees
                img = img.transpose(Image.Transpose.ROTATE_270)
                original_processing_done = True
                print(f"     ✓ Rotated to {img.size[0]}x{img.size[1]}")
            
            # Apply white patch white balance only for new images
            if apply_white_balance:
                print(f"  ⚖️  Applying white patch white balance to {os.path.basename(input_path)}...")
                img = apply_white_patch_white_balance(img)
                original_processing_done = True
                print(f"     ✓ White balance applied")
                
                # Apply auto levels adjustment after white balance
                print(f"  📊 Applying auto levels adjustment to {os.path.basename(input_path)}...")
                img = apply_auto_levels(img)
                print(f"     ✓ Auto levels applied")
            
            # Save processed original back to file if any processing was done
            if original_processing_done:
                img.save(input_path, quality=95, optimize=True)
                print(f"     ✓ Original image updated")
            
            # Calculate new size (20% of processed image)
            original_width, original_height = img.size
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Create thumbnail with high quality resampling
            thumbnail = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with good quality
            if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
                thumbnail.save(output_path, 'JPEG', quality=85, optimize=True)
            elif output_path.lower().endswith('.png'):
                thumbnail.save(output_path, 'PNG', optimize=True)
            else:
                thumbnail.save(output_path, optimize=True)
            
            return True, new_width, new_height
    except Exception as e:
        print(f"Error creating thumbnail for {input_path}: {e}")
        return False, 0, 0

def check_and_fix_thumbnails():
    """Check all thumbnails and recreate if they're not 20% of original size"""
    photos_dir = "photos"
    thumb_dir = os.path.join(photos_dir, "thumb")
    
    if not os.path.exists(photos_dir):
        print(f"Photos directory '{photos_dir}' not found!")
        return
    
    # Create thumb directory if it doesn't exist
    os.makedirs(thumb_dir, exist_ok=True)
    
    # Get list of original images
    original_images = []
    for file in os.listdir(photos_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')) and not file.startswith('.'):
            original_images.append(file)
    
    print(f"Found {len(original_images)} original images")
    
    processed = 0
    created = 0
    fixed = 0
    rotated = 0
    
    for image_file in sorted(original_images):
        original_path = os.path.join(photos_dir, image_file)
        thumb_path = os.path.join(thumb_dir, image_file)
        
        # Check if original image needs rotation first
        needs_rotate = False
        is_new_image = not os.path.exists(thumb_path)  # Only apply white balance to new images
        try:
            with Image.open(original_path) as img:
                needs_rotate = needs_rotation(img)
        except Exception:
            continue
        
        # Get original image size (after potential rotation)
        original_size = get_image_size(original_path)
        if not original_size:
            continue
        
        original_width, original_height = original_size
        expected_thumb_width = int(original_width * 0.2)
        expected_thumb_height = int(original_height * 0.2)
        
        # Check if thumbnail exists and has correct size
        needs_creation = True
        
        # Force recreation if original needs rotation or is new image, or thumbnail has wrong size
        if needs_rotate:
            print(f"🔄 {image_file}: needs rotation + thumbnail" + (" + white balance" if is_new_image else ""))
            rotated += 1
            needs_creation = True
        elif is_new_image:
            print(f"+ {image_file}: new image - applying white balance + creating thumbnail")
            created += 1
            needs_creation = True
        elif os.path.exists(thumb_path):
            thumb_size = get_image_size(thumb_path)
            if thumb_size:
                thumb_width, thumb_height = thumb_size
                # Allow small tolerance (±1 pixel) due to rounding
                if (abs(thumb_width - expected_thumb_width) <= 1 and 
                    abs(thumb_height - expected_thumb_height) <= 1):
                    needs_creation = False
                    print(f"✓ {image_file}: thumbnail OK ({thumb_width}x{thumb_height})")
                else:
                    print(f"✗ {image_file}: wrong size ({thumb_width}x{thumb_height}, expected ~{expected_thumb_width}x{expected_thumb_height})")
                    fixed += 1
        
        if needs_creation:
            success, new_width, new_height = create_thumbnail(original_path, thumb_path, apply_white_balance=is_new_image)
            if success:
                # Re-get original size in case it was rotated
                final_original_size = get_image_size(original_path)
                if final_original_size:
                    final_width, final_height = final_original_size
                    print(f"     → Thumbnail: {new_width}x{new_height} (from {final_width}x{final_height})")
                else:
                    print(f"     → Thumbnail: {new_width}x{new_height}")
            else:
                print(f"     → Failed to create thumbnail")
        
        processed += 1
    
    print(f"\nSummary:")
    print(f"  Processed: {processed} images")
    print(f"  Rotated originals: {rotated}")
    print(f"  New images (with white balance): {created}")
    print(f"  Fixed existing thumbnails: {fixed}")
    print(f"  Already correct: {processed - created - fixed - rotated if processed - created - fixed - rotated >= 0 else 0}")

if __name__ == "__main__":
    check_and_fix_thumbnails()
