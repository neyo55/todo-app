# backend/auth.py
# ProTodo v1.5 - Password Security & Validations

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, User
from mailer import send_reset_code
import random
import string
import os
import re # [v1.5] Regex for password validation
from datetime import datetime, timedelta, timezone

auth_bp = Blueprint('auth', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# [v1.5] PASSWORD VALIDATOR FUNCTION
def is_strong_password(password):
    if len(password) < 8: return False
    if not re.search(r"[A-Z]", password): return False # At least 1 Uppercase
    if not re.search(r"[0-9]", password): return False # At least 1 Number
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False # At least 1 Special
    return True

# SIGNUP ROUTE
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    # [v1.5] Validate Password Strength
    password = data['password']
    if not is_strong_password(password):
        return jsonify({
            "message": "Password too weak. Must be 8+ chars, with 1 uppercase, 1 number, and 1 symbol."
        }), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email taken"}), 400
    
    user = User(
        email=data['email'], 
        name=data.get('name', ''),
        phone=data.get('phone', '')
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Created"}), 201

# LOGIN ROUTE
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        token = create_access_token(identity=str(user.id))
        
        avatar_url = user.avatar
        if avatar_url and not avatar_url.startswith('http') and not avatar_url.startswith('/'):
             avatar_url = f"http://127.0.0.1:5000{user.avatar}"
        elif avatar_url and avatar_url.startswith('/'):
             avatar_url = f"http://127.0.0.1:5000{avatar_url}"

        return jsonify({
            "token": token,
            "user": {
                "name": user.name,
                "nickname": user.nickname,
                "avatar": avatar_url, 
                "email": user.email,
                "phone": user.phone,
                "timezone": user.timezone
            }
        })
    return jsonify({"message": "Invalid credentials"}), 401

# UPDATE PROFILE ROUTE
@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user: return jsonify({"message": "User not found"}), 404
    
    if 'name' in request.form: user.name = request.form['name']
    if 'nickname' in request.form: user.nickname = request.form['nickname']
    if 'phone' in request.form: user.phone = request.form['phone']
    if 'timezone' in request.form: user.timezone = request.form['timezone']
    
    if 'new_password' in request.form and request.form['new_password']:
        new_pass = request.form['new_password']
        if not is_strong_password(new_pass):
            return jsonify({"message": "Password too weak. Must be 8+ chars, 1 Upper, 1 Number, 1 Symbol."}), 400
        user.set_password(new_pass)

    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{user_id}_{file.filename}")
            save_dir = os.path.join(current_app.root_path, 'static', 'avatars')
            os.makedirs(save_dir, exist_ok=True)
            file.save(os.path.join(save_dir, filename))
            user.avatar = f"/static/avatars/{filename}"

    db.session.commit()
    full_avatar_url = f"http://127.0.0.1:5000{user.avatar}" if user.avatar else None
    return jsonify({"message": "Profile updated", "avatar": full_avatar_url})

# FORGET PASSWORD 
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({"message": "If that email exists, a code has been sent."}), 200
    
    code = ''.join(random.choices(string.digits, k=6))
    user.reset_token = code
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
    db.session.commit()
    
    send_reset_code(user.email, code)
    return jsonify({"message": "Reset code sent"}), 200

# RESET PASSWORD
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or user.reset_token != data['code']:
        return jsonify({"message": "Invalid code"}), 400
        
    if user.reset_token_expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return jsonify({"message": "Code expired"}), 400
    
    new_pass = data['new_password']
    if not is_strong_password(new_pass):
        return jsonify({"message": "Password too weak. Must be 8+ chars, 1 Upper, 1 Number, 1 Symbol."}), 400

    user.set_password(new_pass)
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    
    return jsonify({"message": "Password reset successfully"}), 200