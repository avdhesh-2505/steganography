import os
import tensorflow as tf
import numpy as np
import hashlib
from utils.processing import process_image

def calculate_psnr(img1_path, img2_path):
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR) between two images.
    Higher is better (Infinity is perfect).
    """
    img1 = process_image(img1_path)
    img2 = process_image(img2_path)
    
    # MSE (Mean Squared Error)
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    
    # Max pixel value is 1.0 (since we normalized)
    max_pixel = 1.0
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    return psnr

def calculate_ssim(img1_path, img2_path):
    """
    Calculate Structural Similarity Index (SSIM).
    1.0 is perfect similarity.
    """
    img1 = process_image(img1_path)
    img2 = process_image(img2_path)
    
    # Convert from (256, 256, 3) to tensor with batch dim (1, 256, 256, 3)
    im1 = tf.convert_to_tensor(np.expand_dims(img1, axis=0), dtype=tf.float32)
    im2 = tf.convert_to_tensor(np.expand_dims(img2, axis=0), dtype=tf.float32)
    
    ssim = tf.image.ssim(im1, im2, max_val=1.0)
    return float(ssim.numpy()[0])

def check_file_integrity(original_path, recovered_path):
    """
    Compare MD5 hashes of original and recovered files.
    """
    def get_hash(path):
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    hash1 = get_hash(original_path)
    hash2 = get_hash(recovered_path)
    
    print(f"Original MD5 : {hash1}")
    print(f"Recovered MD5: {hash2}")
    
    return hash1 == hash2

if __name__ == '__main__':
    # Interactive Evaluation Script
    print("--- Project Evaluation ---")
    
    # Try to find last processed pair automatically
    processed_dir = 'processed'
    uploads_dir = 'uploads'
    
    # This is a bit manual, assuming user follows the flow. 
    # Let's search for "stego_" files
    from glob import glob
    stego_files = glob(os.path.join(processed_dir, 'stego_*.png'))
    
    if not stego_files:
        print("No stego images found to evaluate. Please run the app and hide a file first.")
    else:
        stego_path = stego_files[0]
        # Infer original cover name path
        # stego_cover.png -> encoded from cover.png (stored in uploads typically, but we need exact name)
        # Simplified: We look for ANY png in uploads as a proxy if we assume 1 file.
        # Better: Read metadata again?
        # Let's read metadata files to find a valid pair.
        
        meta_files = glob(os.path.join(processed_dir, '*_meta.json'))
        if meta_files:
            import json
            import sys
            
            with open(meta_files[0], 'r') as f:
                meta = json.load(f)
                
            original_secret_name = meta['original_filename']
            stego_path = meta['stego_image_path']
            # We don't store original cover path in metadata currently.
            # Assuming it's in uploads/ with same name as in the stego filename (minus "stego_")?
            # stego_path is "processed/stego_Cover.png", so original is "uploads/Cover.png"
            
            stego_basename = os.path.basename(stego_path)
            if stego_basename.startswith("stego_"):
                original_cover_name = stego_basename.replace("stego_", "")
                cover_path = os.path.join(uploads_dir, original_cover_name)
                
                if os.path.exists(cover_path) and os.path.exists(stego_path):
                    print(f"\nEvaluating Image Quality:\nCover: {cover_path}\nStego: {stego_path}")
                    
                    psnr = calculate_psnr(cover_path, stego_path)
                    ssim = calculate_ssim(cover_path, stego_path)
                    
                    print(f"\nResults:")
                    print(f"PSNR: {psnr:.2f} dB (Good > 30, Excellent > 40)")
                    print(f"SSIM: {ssim:.4f} (Max 1.0)")
                else:
                    print(f"Could not find pair: {cover_path} and {stego_path}")

            # 2. File Integrity
            recovered_path = os.path.join(processed_dir, f"recovered_{original_secret_name}")
            secret_path = os.path.join(uploads_dir, original_secret_name)
            
            if os.path.exists(secret_path) and os.path.exists(recovered_path):
                print(f"\nEvaluating File Recovery:\nOriginal: {secret_path}\nRecovered: {recovered_path}")
                is_match = check_file_integrity(secret_path, recovered_path)
                
                if is_match:
                    print("SUCCESS: Files are bit-perfect matches! ✅")
                else:
                    print("FAILURE: Files do not match. ❌ Data corruption occurred.")
            else:
                print("\nRecovered file not found. Process extraction via UI first to test integrity.")
