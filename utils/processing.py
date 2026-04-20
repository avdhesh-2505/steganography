import numpy as np
from PIL import Image

def process_image(image_path, target_size=(256, 256)):
    """
    Load an image, resize it, and normalize to [0, 1].
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img) / 255.0
    return img_array

def save_image(img_array, save_path):
    """
    Save a normalized image array [0, 1] as an image file.
    """
    img_array = np.clip(img_array * 255.0, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_array)
    img.save(save_path)

def bits_to_image(binary_string, target_shape=(256, 256, 3)):
    """
    Convert a binary string (0s and 1s) into an image representation.
    0 -> 0.0, 1 -> 1.0
    If binary string is shorter, pad with 0s.
    If longer, truncate (or handle error).
    """
    total_pixels = target_shape[0] * target_shape[1] * target_shape[2]
    
    # Pad or truncate
    if len(binary_string) < total_pixels:
        binary_string += '0' * (total_pixels - len(binary_string))
    else:
        binary_string = binary_string[:total_pixels]
        
    # Convert string to numpy array
    bits = np.array([int(b) for b in binary_string], dtype=np.float32)
    
    # Reshape to image dimensions
    return bits.reshape(target_shape)

def image_to_bits(img_array):
    """
    Convert an image representation back to binary string.
    > 0.5 -> '1', <= 0.5 -> '0'
    """
    flat = img_array.flatten()
    binary_list = ['1' if pixel > 0.5 else '0' for pixel in flat]
    return "".join(binary_list)
