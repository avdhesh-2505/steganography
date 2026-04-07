from flask import Flask , render_template , url_for , request , redirect,flash,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash , check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import json
import binascii
from flask import Flask, render_template, request, flash, redirect, url_for,send_from_directory
#from utils.crypto import AESCipher
#from utils.binary import bytes_to_binary, binary_to_bytes
#from utils.steganography import embed_secret, extract_secret

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'
app.secret_key='super_secret_key_for_session'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

class User(db.Model):
        id=db.Column(db.Integer,primary_key=True)
        name=db.Column(db.String(100))
        email=db.Column(db.String(120),unique=True)
        password=db.Column(db.String(200))
with app.app_context():
        db.create_all()

# Configuration
# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {'png'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'txt'}
MAX_FILE_SIZE = 1 * 1024 * 1024 # 1 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename,allowed_extensions):
        return '.' in filename and filename.rsplit('.',1)[1].lower() in allowed_extensions

@app.route('/')
def index():
        return render_template('index.html') 

def login_required(f):
        @wraps(f)
        def decorated(*args,**kwargs):
                if 'user_id' not in session:
                        flash('Please login to access this page','error')
                        return redirect(url_for('login'))
                return f(*args,**kwargs)
        return decorated

@app.route('/login',methods=['GET','POST'])    #login page
def login():
        if request.method=='POST':
                email=request.form.get('email')
                password=request.form.get('password')
                user=User.query.filter_by(email=email).first()
                if user and check_password_hash(user.password,password):
                        session['user_id']=user.id
                        session['user_name']=user.name
                        flash('Signin successful','success')
                        return redirect(url_for('upload'))
                else:
                        flash('Invalid email or password','error')
        return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if'cover_image' not in request.files or 'secret_file' not in request.files:
                flash('No file part','error')
                return redirect(request.url)

        cover_image = request.files['cover_image']
        secret_file = request.files['secret_file']

        # 1. Validation
        if cover_image.filename == '' or secret_file.filename == '':
                flash('Files not selected', 'error')
                return redirect(request.url)
        if not allowed_file(cover_image.filename, ALLOWED_IMAGE_EXTENSIONS):
                flash('Invalid image format. Only PNG is allowed.', 'error')
                return redirect(request.url)
        if not allowed_file(secret_file.filename, ALLOWED_DOC_EXTENSIONS):
                flash('Invalid secret file format. Only PDF or TXT allowed.', 'error')
                return redirect(request.url)
        
        # 4. Save and Start Processing
        image_filename = secure_filename(cover_image.filename)
        secret_filename = secure_filename(secret_file.filename)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        secret_path = os.path.join(app.config['UPLOAD_FOLDER'], secret_filename)
        
        cover_image.save(cover_path)
        secret_file.save(secret_path)

        try:
            # Re-enabling imports (wrapped in try/except)
            from utils.crypto import AESCipher
            from utils.binary import bytes_to_binary, add_error_correction
            from utils.steganography import embed_secret

            aes = AESCipher()
            encrypted_bytes, iv, key = aes.encrypt_file(secret_path)
            raw_binary_string = bytes_to_binary(encrypted_bytes)

            # Error Correction
            encoded_binary_string = add_error_correction(raw_binary_string, n=5)

            # Save Metadata
            metadata = {
                'original_filename': secret_filename,
                'key': binascii.hexlify(key).decode('utf-8'),
                'iv': binascii.hexlify(iv).decode('utf-8'),
                'binary_length': len(encoded_binary_string)
            }

            metadata_path = os.path.join(PROCESSED_FOLDER, f"{secret_filename}_meta.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)

            # Generate Stego Image
            stego_filename = f"stego_{image_filename}"
            stego_path = os.path.join(PROCESSED_FOLDER, stego_filename)
            embed_secret(cover_path, encoded_binary_string, stego_path)

            metadata['stego_image_path'] = stego_path
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)

            flash(f'Steganography Complete!', 'success')
            return render_template('uploads.html', stego_filename=stego_filename)
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
            return redirect(url_for('upload'))

    return render_template('uploads.html')

# Download Route
@app.route('/download/<filename>')
def download_file(filename):
        return send_from_directory('processed', filename, as_attachment=True)


@app.route('/register',methods=['GET','POST'])    #register page
def register():
        if request.method=='POST':
                name=request.form.get('name')
                email=request.form.get('email')
                password=request.form.get('password')
                confirm_password=request.form.get('confirm_password')

                if not name or len(name.strip())<2:
                        flash('name must be atleast 2 character long','error')
                        return redirect(url_for('register'))
                if not email or '@' not in email :
                        flash('Invalid email','error')
                        return redirect(url_for('register'))
                if not password or len(password)<8 or not any(char.isalpha() for char in password ) or not any(char.isdigit() for char in password) or not any (not char.isalnum() for char in password):
                        flash('pass must be atleast 8 char long and contain letters and contain numbers and special characters','error')
                        return redirect(url_for('register'))
                if confirm_password!=password:
                        flash('Confirm password should match password','error')
                        return redirect(url_for('register'))
                #check if user already exists
                existing_user=User.query.filter_by(email=email).first()
                if existing_user:
                        flash('Email already exists.Please login. ','error')
                        return redirect(url_for('register'))
                # generate hash password
                hashed_password=generate_password_hash(password)
                new_user=User(
                        name=name.strip(),
                        email=email.strip(),
                        password=hashed_password
                )
                try:
                        db.session.add(new_user)
                        db.session.commit()
                        flash('Registration successful .Proceed to signin','success')
                        return redirect(url_for('login'))
                except Exception as e:
                        db.session.rollback()
                        flash('Some error occured while registering','error')
                        return redirect(url_for('register'))

        return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully','success')
    return redirect(url_for('login'))


if __name__=='__main__':
        app.run(debug=True , host='0.0.0.0')
