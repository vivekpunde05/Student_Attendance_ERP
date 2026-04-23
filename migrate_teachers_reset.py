from connection import execute

print("Adding reset columns to teachers table...")
try:
    execute("ALTER TABLE teachers ADD COLUMN reset_token VARCHAR(64) NULL", commit=True)
    print("✓ reset_token added")
except Exception as e:
    print(f"reset_token exists: {e}")

try:
    execute("ALTER TABLE teachers ADD COLUMN reset_expires DATETIME NULL", commit=True)
    print("✓ reset_expires added")
except Exception as e:
    print(f"reset_expires exists: {e}")

print("Verifying teachers reset columns...")
result = execute("DESCRIBE teachers", fetch=True)
for row in result:
    if 'reset' in row['Field'].lower():
        print(f"✓ {row['Field']}: {row['Type']}")

print("Migration complete! Now teacher forgot password will work.")

