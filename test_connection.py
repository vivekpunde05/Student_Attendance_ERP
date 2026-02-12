#!/usr/bin/env python3
"""Test script to verify Aiven MySQL connection"""

from connection import get_conn
from config import DB_CONFIG

def test_connection():
    print("Testing Aiven MySQL connection...")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"User: {DB_CONFIG['user']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Port: {DB_CONFIG['port']}")
    print(f"SSL Enabled: {not DB_CONFIG['ssl_disabled']}")
    print("-" * 50)
    
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✓ Connection successful!")
        print(f"✓ MySQL version: {version[0]}")
        
        cursor.execute("SELECT DATABASE()")
        db = cursor.fetchone()
        print(f"✓ Connected to database: {db[0]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
