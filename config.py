import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "ssl_disabled": False,
    "connect_timeout": 30,
    "autocommit": False
}

# Debug: Print config (without password) to verify environment variables are loaded
print(f"DB Config - Host: {DB_CONFIG['host']}, User: {DB_CONFIG['user']}, Database: {DB_CONFIG['database']}, Port: {DB_CONFIG['port']}")
