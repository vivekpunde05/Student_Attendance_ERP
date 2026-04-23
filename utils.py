import os
import hashlib
from datetime import datetime

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + dk.hex()

def verify_password(stored: str, password: str) -> bool:
    salt = bytes.fromhex(stored[:32])
    dk = stored[32:]
    test = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return test.hex() == dk

def now_date_str():
    return datetime.now().strftime('%Y-%m-%d')

def now_time_str():
    return datetime.now().strftime('%H:%M:%S')

def validate_password_length(password: str) -> tuple[bool, str]:
    """Validate password length >=8. Returns (valid, error_msg)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, ""

def generate_secure_password(length: int = 12) -> str:
    """Generate cryptographically secure random password using Python secrets library"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
            return password


# Email imports for forgot password (lazy loaded)
def _get_email_modules():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import uuid
    from datetime import timedelta
    from config import EMAIL_CONFIG
    return locals()

def generate_reset_token() -> str:
    """Generate secure reset token"""
    import uuid
    return str(uuid.uuid4().hex)

def send_reset_email(email: str, username: str, reset_token: str, is_admin: bool = False):
    """Send password reset email"""
    modules = _get_email_modules()
    smtplib = modules['smtplib']
    MIMEText = modules['MIMEText']
    MIMEMultipart = modules['MIMEMultipart']
    EMAIL_CONFIG = modules['EMAIL_CONFIG']
    
    if not EMAIL_CONFIG['username'] or not EMAIL_CONFIG['password']:
        print("Email config missing - skipping send")
        return False
    
    role = "Admin" if is_admin else "Teacher"
    reset_url = f"http://localhost:5000/reset-password/{reset_token}"
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG['from_email']
    msg['To'] = email
    msg['Subject'] = f"{role} Password Reset"
    
    body = f"""
Dear {username},
Reset link (1hr valid): {reset_url}
Ignore if not requested.
Attendance ERP
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
