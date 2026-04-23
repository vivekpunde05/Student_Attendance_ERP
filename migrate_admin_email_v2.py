"""
Migration: Add email column to admins table
Required for Password Reset v2 system
"""
from connection import init_pool, execute

def migrate():
    init_pool()
    
    # Check if email column exists
    try:
        result = execute("SHOW COLUMNS FROM admins LIKE 'email'", fetch=True)
        if result:
            print("email column already exists in admins table")
            return
    except Exception as e:
        print(f"Error checking columns: {e}")
    
    # Add email column
    try:
        execute("ALTER TABLE admins ADD COLUMN email VARCHAR(100) UNIQUE", commit=True)
        print("✅ email column added to admins table")
        
        # Update default admin with a placeholder email
        execute("UPDATE admins SET email = 'admin@attendance-erp.local' WHERE email IS NULL", commit=True)
        print("✅ Default admin email set")
        
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == '__main__':
    migrate()

