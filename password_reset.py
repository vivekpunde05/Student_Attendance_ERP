"""
Complete Password Reset System for Flask + MySQL
Features:
- Email-based reset requests
- Secure token generation (secrets module)
- Token storage with expiry (30 min)
- bcrypt password hashing
- Single-use token invalidation
- SMTP email sending
- Full error handling
"""

import os
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import bcrypt
from connection import execute

# Create Blueprint
password_reset_bp = Blueprint('password_reset', __name__, template_folder='templates')

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def create_reset_tokens_table():
    """Create password_reset_tokens table if not exists"""
    execute("""
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(100) NOT NULL,
        token VARCHAR(64) UNIQUE NOT NULL,
        user_type ENUM('admin','teacher') NOT NULL,
        user_id INT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        used BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_token (token),
        INDEX idx_email (email)
    ) ENGINE=InnoDB;
    """, commit=True)
    print("password_reset_tokens table ready")


def store_reset_token(email: str, token: str, user_type: str, user_id: int, expiry_minutes: int = 30):
    """Store reset token in database with expiry"""
    expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
    execute(
        """INSERT INTO password_reset_tokens (email, token, user_type, user_id, expires_at)
           VALUES (%s, %s, %s, %s, %s)""",
        (email, token, user_type, user_id, expires_at),
        commit=True
    )


def get_token_record(token: str):
    """Get token record by token string"""
    result = execute(
        """SELECT * FROM password_reset_tokens 
           WHERE token = %s AND used = FALSE AND expires_at > NOW()""",
        (token,), fetch=True
    )
    return result[0] if result else None


def mark_token_used(token: str):
    """Invalidate token after use (single-use)"""
    execute(
        "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s",
        (token,), commit=True
    )


def delete_expired_tokens():
    """Clean up expired tokens"""
    execute(
        "DELETE FROM password_reset_tokens WHERE expires_at < NOW() OR used = TRUE",
        commit=True
    )


# ============================================================================
# USER LOOKUP FUNCTIONS
# ============================================================================

def find_user_by_email(email: str):
    """Find admin or teacher by email. Returns (user_type, user_data) or (None, None)"""
    # Check admin first
    admin = execute("SELECT * FROM admins WHERE email = %s", (email,), fetch=True)
    if admin:
        return 'admin', admin[0]
    
    # Check teacher
    teacher = execute("SELECT * FROM teachers WHERE email = %s", (email,), fetch=True)
    if teacher:
        return 'teacher', teacher[0]
    
    return None, None


# ============================================================================
# TOKEN & HASHING UTILITIES
# ============================================================================

def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token using secrets"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_password_bcrypt(password: str) -> str:
    """Hash password using bcrypt (adaptive, salt automatically included)"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password_bcrypt(stored_hash: str, password: str) -> bool:
    """Verify password against bcrypt hash"""
    password_bytes = password.encode('utf-8')
    stored_bytes = stored_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, stored_bytes)


# ============================================================================
# EMAIL FUNCTION
# ============================================================================

def send_reset_email(to_email: str, username: str, token: str, user_type: str):
    """Send password reset email via SMTP"""
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_pass = os.environ.get('SMTP_PASS', '')
    from_email = os.environ.get('FROM_EMAIL', smtp_user)
    
    if not smtp_user or not smtp_pass:
        print(f"[EMAIL DEBUG] SMTP not configured. Token for {username}: {token}")
        return False
    
    reset_url = f"http://localhost:5000/reset-password-v2?token={token}"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Password Reset Request - Attendance ERP'
    msg['From'] = from_email
    msg['To'] = to_email
    
    text_body = f"""Hello {username},

You requested a password reset for your {user_type.upper()} account.

Reset your password here (valid for 30 minutes):
{reset_url}

If you did not request this, please ignore this email.

Attendance ERP System
"""
    
    html_body = f"""<!DOCTYPE html>
<html>
<head><style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
.container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
.button {{ display: inline-block; padding: 12px 24px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; margin: 15px 0; }}
.footer {{ color: #999; font-size: 12px; margin-top: 30px; }}
</style></head>
<body>
<div class="container">
    <h2>Password Reset Request</h2>
    <p>Hello <strong>{username}</strong>,</p>
    <p>You requested a password reset for your <strong>{user_type.upper()}</strong> account.</p>
    <a href="{reset_url}" class="button">Reset My Password</a>
    <p>Or copy this link:<br><code>{reset_url}</code></p>
    <p>This link expires in <strong>30 minutes</strong> and can only be used once.</p>
    <div class="footer">
        If you did not request this, please ignore this email.<br>
        Attendance ERP System
    </div>
</div>
</body>
</html>"""
    
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"[EMAIL SENT] Reset link sent to {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


# ============================================================================
# UPDATE PASSWORD FUNCTIONS
# ============================================================================

def update_user_password(user_type: str, user_id: int, new_password: str):
    """Update password with bcrypt hash for admin or teacher"""
    hashed = hash_password_bcrypt(new_password)
    if user_type == 'admin':
        execute("UPDATE admins SET password_hash = %s WHERE id = %s", (hashed, user_id), commit=True)
    elif user_type == 'teacher':
        execute("UPDATE teachers SET password_hash = %s WHERE id = %s", (hashed, user_id), commit=True)


# ============================================================================
# FLASK ROUTES
# ============================================================================

@password_reset_bp.route('/forgot-password-v2', methods=['GET', 'POST'])
def forgot_password_v2():
    """Step 1: User enters email to request password reset"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address', 'error')
            return redirect(url_for('password_reset.forgot_password_v2'))
        
        # Find user by email
        user_type, user = find_user_by_email(email)
        
        if not user:
            # Security: Don't reveal if email exists
            flash('If this email is registered, you will receive a reset link shortly.', 'success')
            return redirect(url_for('password_reset.forgot_password_v2'))
        
        try:
            # Generate secure token
            token = generate_secure_token(32)
            
            # Store token with 30-min expiry
            store_reset_token(email, token, user_type, user['id'], expiry_minutes=30)
            
            # Send email
            sent = send_reset_email(email, user.get('full_name') or user.get('username'), token, user_type)
            
            if sent:
                flash('Reset link sent! Check your email (valid for 30 minutes).', 'success')
            else:
                # Development mode: show reset link directly when SMTP not configured
                reset_url = f"http://localhost:5000/reset-password-v2?token={token}"
                flash(f'Email service not configured. Use this reset link (copy & paste): {reset_url}', 'warning')
                print(f"[DEBUG] Reset URL: {reset_url}")
            
        except Exception as e:
            current_app.logger.error(f"Password reset error: {e}")
            flash('An error occurred. Please try again later.', 'error')
        
        return redirect(url_for('password_reset.forgot_password_v2'))
    
    return render_template('password_reset/request_reset.html')


@password_reset_bp.route('/reset-password-v2', methods=['GET', 'POST'])
def reset_password_v2():
    """Step 2: User clicks email link and sets new password"""
    token = request.args.get('token') or request.form.get('token')
    
    if not token:
        flash('Invalid reset link. Please request a new one.', 'error')
        return redirect(url_for('password_reset.forgot_password_v2'))
    
    # Verify token
    record = get_token_record(token)
    
    if not record:
        # Check if token exists but expired/used
        check = execute("SELECT * FROM password_reset_tokens WHERE token = %s", (token,), fetch=True)
        if check:
            if check[0]['used']:
                flash('This reset link has already been used. Please request a new one.', 'error')
            else:
                flash('This reset link has expired. Please request a new one.', 'error')
        else:
            flash('Invalid reset link. Please request a new one.', 'error')
        return redirect(url_for('password_reset.forgot_password_v2'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('password_reset/do_reset.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('password_reset/do_reset.html', token=token)
        
        try:
            # Update password with bcrypt
            update_user_password(record['user_type'], record['user_id'], new_password)
            
            # Invalidate token (single-use)
            mark_token_used(token)
            
            flash('Password reset successful! Please login with your new password.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            current_app.logger.error(f"Password update error: {e}")
            flash('An error occurred while updating your password.', 'error')
            return render_template('password_reset/do_reset.html', token=token)
    
    # GET: Show reset form
    return render_template('password_reset/do_reset.html', token=token)


@password_reset_bp.route('/reset-success')
def reset_success():
    """Success confirmation page"""
    return render_template('password_reset/success.html')
