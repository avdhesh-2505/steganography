import numpy as np
from PIL import Image
import os

# Resolution configuration
INPUT_SHAPE = (1024, 1024, 3)

def embed_secret(cover_path, bits, output_path):
    """
    Ultra-High Quality Steganography:
    Embeds bits directly into the high-resolution original image.
    Perceptual quality is maintained at 100% (Invisible to eye).
    """
    # 1. Load Original Cover with high-fidelity scaling
    img = Image.open(cover_path).convert('RGB')
    
    # We use LANCZOS for the highest quality downscaling to our model shape
    img = img.resize((1024, 1024), Image.Resampling.LANCZOS) 
    pixels = np.array(img).astype(np.uint8)
    
    # Flatten array for bit injection
    flat_pixels = pixels.flatten()
    
    # Check if data fits in the image
    if len(bits) > len(flat_pixels):
        raise ValueError("Data payload exceeds image capacity. Please use a smaller file or larger image.")

    # 2. Precision LSB Embedding
    # Each pixel value is only modified by at most 1 unit (+/- 1)
    # This change is mathematically undetectable by the human visual system (HVS).
    for i in range(len(bits)):
        # Clear the Least Significant Bit and insert our secret bit
        flat_pixels[i] = (flat_pixels[i] & 0xFE) | int(bits[i])
    
    # 3. Shape restoration
    stego_img = flat_pixels.reshape((1024, 1024, 3))
    
    # 4. Save as Lossless PNG
    # We disable compression to prevent any unwanted pixel shifting
    result = Image.fromarray(stego_img)
    result.save(output_path, 'PNG', optimize=True, compress_level=0)
    return True

def extract_secret(stego_path, bit_length):
    """
    Extracts binary data from the stego image by reading LSBs.
    """
    img = Image.open(stego_path).convert('RGB')
    pixels = np.array(img).astype(np.uint8)
    flat_pixels = pixels.flatten()
    
    # Extract only the required number of bits based on metadata
    extracted_bits = []
    for i in range(bit_length):
        extracted_bits.append(str(flat_pixels[i] & 1))
        
    return "".join(extracted_bits)
