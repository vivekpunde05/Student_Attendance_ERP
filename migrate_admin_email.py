from connection import execute

print("Adding email column to admins...")
try:
    execute("ALTER TABLE admins ADD COLUMN email VARCHAR(100) NULL AFTER full_name", commit=True)
    print("Email column added")
except Exception as e:
    print(f"Column exists or error: {e}")

print("Updating admin email...")
execute("UPDATE admins SET email = 'vivekpunde6@gmail.com' WHERE username = 'admin'", commit=True)

print("Verifying...")
result = execute("SELECT username, email FROM admins WHERE username = 'admin'", fetch=True)
print(result)

print("Migration complete!")
