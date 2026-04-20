import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class AESCipher:
    def __init__(self):
        # A static master secret used internally for all encryptions.
        # Access is protected by ADMIN_KEY and USER_KEY in app.py
        self.master_secret = hashlib.sha256(b"PROJECT_STEGO_MASTER_KEY_2026").digest()

    def encrypt_file(self, file_path):
        """Encrypts a file using the internal master secret."""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        iv = get_random_bytes(16)
        cipher = AES.new(self.master_secret, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        
        return encrypted_data, iv, self.master_secret

    def decrypt_data(self, encrypted_data, iv):
        """Decrypts data using the internal master secret."""
        try:
            cipher = AES.new(self.master_secret, AES.MODE_CBC, iv)
            decrypted_padded = cipher.decrypt(encrypted_data)
            
            try:
                decrypted_data = unpad(decrypted_padded, AES.block_size)
                return decrypted_data
            except ValueError:
                # Still handle noise just in case
                return decrypted_padded
        except Exception as e:
            raise e
