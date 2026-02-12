import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "ssl_disabled": False,
    "ssl_verify_cert": False,  # Set to False for Aiven without CA cert file
    "ssl_verify_identity": False
}
