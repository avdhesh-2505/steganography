import os
import numpy as np
import tensorflow as tf
from models.architecture import get_steganography_model
from models.losses import stego_loss, secret_loss
from utils.processing import process_image
from glob import glob

# Configuration
EPOCHS = 50  # Keep it small for demonstration/speed
BATCH_SIZE = 4 # Reduced batch size for larger images
INPUT_SHAPE = (1024, 1024, 3)
DATASET_PATH = 'dataset' # Or 'uploads' for user images
MODEL_SAVE_PATH = 'models/stego_model.weights.h5' # New Keras format

def train_model():
    # 1. Prepare Data
    image_paths = glob(os.path.join(DATASET_PATH, '*.png')) + glob(os.path.join(DATASET_PATH, '*.jpg'))
    if not image_paths:
        print("No images found in 'dataset/'. Checking 'uploads/'...")
        image_paths = glob(os.path.join('uploads', '*.png'))
    
    if not image_paths:
        print("ERROR: No images found. Please upload at least one image via the UI first.")
        return

    print(f"Found {len(image_paths)} source images.")

    # Load all images into memory
    images = []
    for path in image_paths:
        try:
            img = process_image(path, target_size=INPUT_SHAPE[:2])
            images.append(img)
        except Exception as e:
            print(f"Skipping {path}: {e}")
    
    if not images:
        print("No valid images loaded.")
        return

    # Create a larger dataset by repeating images or augmenting if needed
    # For this demo, we'll create a fixed dataset of, say, 100 samples
    num_samples = 100
    X_cover = []
    X_secret = []
    
    print("Generating synthetic training data...")
    import random
    for i in range(num_samples):
        # Pick a random cover image
        cover = random.choice(images)
        X_cover.append(cover)
        
        # Generate random secret bits (as image)
        secret = np.random.randint(0, 2, size=INPUT_SHAPE).astype(np.float32)
        X_secret.append(secret)
        
    X_cover = np.array(X_cover)
    X_secret = np.array(X_secret)
    
    print(f"Dataset Shape: {X_cover.shape}")

    # 3. Model Setup
    model = get_steganography_model(INPUT_SHAPE)
    
    model.compile(optimizer='adam', 
                  loss=[stego_loss, secret_loss],
                  loss_weights=[1.0, 1.0])

    # 4. Train
    print("Starting Training (Simple Numpy Mode)...")
    model.fit(
        x=[X_cover, X_secret],
        y=[X_cover, X_secret],
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        verbose=1
    )

    # 5. Save Model
    model.save_weights(MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")

if __name__ == '__main__':
    train_model()
