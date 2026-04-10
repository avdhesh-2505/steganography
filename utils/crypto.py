from Crypto.Cipher import AES 
from Crypto.Util.Padding import pad, unpad 
from Crypto.Random import get_random_bytes 
import os

class AESCipher: 
 def __init__(self, key=None):
    self.key = key if key else get_random_bytes(32)

def encrypt_file(self, file_path):
   """ 
Reads a file, encrypts its content using AES-CBC. 
        Returns:  
            encrypted_data (bytes): The ciphertext 
            iv (bytes): Initialization Vector 
            key (bytes): The secret key used 
        """ 
   with open(file_path, 'rb') as f:
    data = f.read()

    iv = get_random_bytes(16)
    cipher = AES.new(self.key, AES.MODE_CBC, iv) 
    encrypted_data = cipher.encrypt(pad(data, AES.block_size)) 
    return encrypted_data, iv, self.key
         
def decrypt_data(self, encrypted_data, key, iv): 
        """ 
        Decrypts data using AES-CBC. 
        Handles padding errors gracefully for Deep Learning based steganography 
        (since neural nets might introduce bit errors). 
        """ 
        try: 
            cipher = AES.new(key, AES.MODE_CBC, iv) 
            decrypted_padded = cipher.decrypt(encrypted_data) 
             
            try: 
                decrypted_data = unpad(decrypted_padded, AES.block_size) 
                return decrypted_data 
            except ValueError: 
                # Padding error: significant bit corruption occurred during extraction. 
                # We return the raw data (best effort) instead of crashing. 
                print("Warning: Padding Incorrect. Returning best-effort decryption.") 
                return decrypted_padded 
        except Exception as e: 
            raise e 

