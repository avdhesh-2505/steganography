import os 
import json 
import binascii 
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory 
from werkzeug.utils import secure_filename 
from utils.crypto import AESCipher 
from utils.binary import bytes_to_binary, binary_to_bytes 
from utils.steganography import embed_secret, extract_secret 


app = Flask(__name__) 
app.secret_key = 'super_secret_key_for_session'  # Required for flash messages 

# Configuration 
UPLOAD_FOLDER = 'uploads' 
ALLOWED_IMAGE_EXTENSIONS = {'png'} 
ALLOWED_DOC_EXTENSIONS = {'pdf', 'txt'} 
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB 

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 

def allowed_file(filename, allowed_extensions): 
    return '.' in filename and \
          filename.rsplit('.', 1)[1].lower() in allowed_extensions 

@app.route('/') 
def home(): return render_template('index.html') 
@app.route('/upload', methods=['POST']) 
def upload_files(): 
    if 'cover_image' not in request.files or 'secret_file' not in request.files: 
        flash('No file part', 'error') 
        return redirect(request.url) 
     
    cover_image = request.files['cover_image'] 
    secret_file = request.files['secret_file'] 
 
    # 1. Validate Cover Image 
    if cover_image.filename == '': 
        flash('No selected cover image', 'error') 
        return redirect(request.url) 
     
    if not allowed_file(cover_image.filename, ALLOWED_IMAGE_EXTENSIONS): 
        flash('Invalid image format. Only PNG is allowed.', 'error') 
        return redirect(request.url) 
 
    # 2. Validate Secret File 
    if secret_file.filename == '': 
        flash('No selected secret file', 'error') 
        return redirect(request.url) 
     
    if not allowed_file(secret_file.filename, ALLOWED_DOC_EXTENSIONS): 
        flash('Invalid secret file format. Only PDF or TXT allowed.', 'error') 
        return redirect(request.url) 
 
    # 3. Check File Size (Reading the file pointer) 
    secret_file.seek(0, os.SEEK_END) 
    file_size = secret_file.tell() 
    secret_file.seek(0)  # Reset pointer to beginning 
 
    if file_size > MAX_FILE_SIZE: 
        flash(f'Secret file is too large ({file_size/1024:.2f} KB). Max allowed is 1 MB.', 'error') 
        return redirect(request.url) 
 
    # 4. Save Files 
    image_filename = secure_filename(cover_image.filename) 
    secret_filename = secure_filename(secret_file.filename) 
     
    cover_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename) 
    secret_path = os.path.join(app.config['UPLOAD_FOLDER'], secret_filename) 
 
    cover_image.save(cover_path) 
    secret_file.save(secret_path) 
 
    # 5. Encrypt Secret File 
    # Generate a new random key for this session/file 
    aes = AESCipher()  
    encrypted_bytes, iv, key = aes.encrypt_file(secret_path) 
 
    # Convert encrypted bytes to binary string (0s and 1s) for steganography 
    raw_binary_string = bytes_to_binary(encrypted_bytes) 
 
    # Apply Error Correction (Repetition Code) to survive Neural Noise 
    # This helps fix the "Corrupted File" issue 
    from utils.binary import add_error_correction 
    encoded_binary_string = add_error_correction(raw_binary_string, n=5) 
 
    # Save the encoded binary string to a file 
    processed_filename = f"encrypted_{secret_filename}.bin" 
    processed_path = os.path.join('processed', processed_filename) 
     
    with open(processed_path, 'w') as f: 
        f.write(encoded_binary_string) 
 
    # Store metadata (Key, IV) so we can decrypt later 
    metadata = { 
        'original_filename': secret_filename, 
        'encrypted_binary_path': processed_path, 
        'key': binascii.hexlify(key).decode('utf-8'), 
        'iv': binascii.hexlify(iv).decode('utf-8'), 
        'binary_length': len(encoded_binary_string) # Store length of ENCODED bits 
    } 
     
    metadata_path = os.path.join('processed', f"{secret_filename}_meta.json") 
    with open(metadata_path, 'w') as f: 
        json.dump(metadata, f, indent=4) 
 
    # 6. Deep Learning Embedding 
    stego_filename = f"stego_{image_filename}" 
    stego_path = os.path.join('processed', stego_filename) 
     
    # Use the encoded binary string we just generated 
    embed_secret(cover_path, encoded_binary_string, stego_path) 
 
    # Update metadata with stego image location 
    metadata['stego_image_path'] = stego_path 
    with open(metadata_path, 'w') as f: 
        json.dump(metadata, f, indent=4) 
 
    flash(f'Steganography Complete!', 'success') 
    return render_template('index.html', stego_filename=stego_filename) 
 
@app.route('/extract-page') 
def extract_page(): 
    return render_template('extract.html') 
 
@app.route('/upload-extract', methods=['POST']) 
def upload_extract(): 
    stego_image = request.files['stego_image'] 
    original_name = request.form['original_name'] 
     
    if stego_image.filename == '': 
        flash('No file selected', 'error') 
        return redirect(url_for('extract_page')) 
 
    stego_filename = secure_filename(stego_image.filename) 
    stego_path = os.path.join('processed', stego_filename) 
    stego_image.save(stego_path) 
     
    metadata_path = os.path.join('processed', f"{original_name}_meta.json") 
    if not os.path.exists(metadata_path): 
        flash(f"No metadata found for '{original_name}'. Cannot decrypt without the key.", 
'error') 
        return redirect(url_for('extract_page')) 
 
    return redirect(url_for('extract_file', filename=original_name)) 
 
@app.route('/extract/<filename>') 
def extract_file(filename): 
    # 1. Load Metadata 
    metadata_path = os.path.join('processed', f"{filename}_meta.json") 
    if not os.path.exists(metadata_path): 
        flash('Metadata not found.', 'error') 
        return redirect(url_for('extract_page')) 
 
    with open(metadata_path, 'r') as f: 
        metadata = json.load(f) 
 
    stego_path = metadata.get('stego_image_path') 
     
    if not stego_path or not os.path.exists(stego_path): 
        flash(f'Stego image file not found at {stego_path}', 'error') 
        return redirect(url_for('extract_page')) 
 
    key = binascii.unhexlify(metadata['key']) 
    iv = binascii.unhexlify(metadata['iv']) 
    bit_length = metadata['binary_length'] 
 
    # 2. Extraction 
    try: 
        extracted_encoded_string = extract_secret(stego_path, bit_length=bit_length) 
    except Exception as e: 
         flash(f'Extraction failed: {e}', 'error') 
         return redirect(url_for('extract_page')) 
 
    # 3. Convert & Decrypt 
    try: 
        # Remove Error Correction (Majority Vote) 
        from utils.binary import remove_error_correction 
        cleaned_binary_string = remove_error_correction(extracted_encoded_string, n=5) 
         
        encrypted_bytes = binary_to_bytes(cleaned_binary_string) 
        aes = AESCipher() 
        decrypted_data = aes.decrypt_data(encrypted_bytes, key, iv) 
    except Exception as e: 
        flash(f'Decryption failed: {e}', 'error') 
        return redirect(url_for('extract_page')) 
 
    # 5. Save 
    recovered_filename = f"recovered_{metadata['original_filename']}" 
    recovered_path = os.path.join('processed', recovered_filename) 
     
    with open(recovered_path, 'wb') as f: 
        f.write(decrypted_data) 
        
        flash('Success! File recovered successfully.', 'success') 
        return render_template('index.html', recovered_filename=recovered_filename)
    
    @app.route('/download/<filename>')
    def download_file(filename): 
        return send_from_directory('processed', filename, as_attachment=True)
    
    if __name__ == '__main__':
    # Running with use_reloader=False to prevent TensorFlow from triggering a restart loop 
     app.run(debug=True, use_reloader=False)   
