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
