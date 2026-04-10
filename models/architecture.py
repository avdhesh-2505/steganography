import tensorflow as tf
from tensorflow.keras import layers, models, Input

def make_encoder(input_shape=(256, 256, 3)):
    """
    Encoder: Takes Cover Image + Secret Data and generates Stego Image.
    Input:
    - Cover Image (HxWx3)
    - Secret Data (HxWx3) - The binary payload converted to an image representation
    Output:
    - Stego Image (HxWx3)
    """
    # Two inputs: Cover and Secret
    cover_input = Input(shape=input_shape, name='cover_input')
    secret_input = Input(shape=input_shape, name='secret_input')

    # Concatenate inputs to process them together
    x = layers.Concatenate()([cover_input, secret_input])

    # Block 1
    x = layers.Conv2D(32, (3, 3), padding='same', activation='relu')(x)
    x = layers.Conv2D(32, (3, 3), padding='same', activation='relu')(x)
    
    # Block 2
    x = layers.Conv2D(64, (3, 3), padding='same', activation='relu')(x)
    x = layers.Conv2D(64, (3, 3), padding='same', activation='relu')(x)
    
    # Block 3
    x = layers.Conv2D(128, (3, 3), padding='same', activation='relu')(x)
    x = layers.Conv2D(128, (3, 3), padding='same', activation='relu')(x)
    
    # Output Layer - 3 channels for RGB Stego Image
    # Sigmoid activation to keep pixel values between 0 and 1
    stego_output = layers.Conv2D(3, (3, 3), padding='same', activation='sigmoid', name='stego_output')(x)  
    
    return models.Model(inputs=[cover_input, secret_input], outputs=stego_output, name='Encoder') 

def make_decoder(input_shape=(256, 256, 3)):
    """
    Decoder: Takes Stego Image and extracts Secret Data.
    Input:
    - Stego Image (HxWx3)
    Output:
    - Revealed Secret (HxWx3)
    """  
    stego_input = Input(shape=input_shape, name='stego_input')
    
    # Block 1
    x = layers.Conv2D(128, (3, 3), padding='same', activation='relu')(stego_input)
    x = layers.Conv2D(128, (3, 3), padding='same', activation='relu')(x)
    
    # Block 2
    x = layers.Conv2D(64, (3, 3), padding='same', activation='relu')(x)
    x = layers.Conv2D(64, (3, 3), padding='same', activation='relu')(x)
    
    # Block 3
    x = layers.Conv2D(32, (3, 3), padding='same', activation='relu')(x)
    x = layers.Conv2D(32, (3, 3), padding='same', activation='relu')(x)
    
    # Output Layer - 3 channels to reconstruct the Secret "Image"
    reveal_output = layers.Conv2D(3, (3, 3), padding='same', activation='sigmoid', name='reveal_output')(x)
    
    return models.Model(inputs=stego_input, outputs=reveal_output, name='Decoder')

def get_steganography_model(input_shape=(256, 256, 3)):
    """
    Combined Autoencoder Model for Training.
    """
    encoder = make_encoder(input_shape)
    decoder = make_decoder(input_shape)

    cover_input = Input(shape=input_shape)
    secret_input = Input(shape=input_shape)
    
    stego_img = encoder([cover_input, secret_input])
    revealed_secret = decoder(stego_img)
    
    return models.Model(inputs=[cover_input, secret_input], outputs=[stego_img, revealed_secret], name='StegoNet')