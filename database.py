from connection import execute
import utils

def create_tables():
    execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password_hash VARCHAR(512),
        full_name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """, commit=True)

    execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password_hash VARCHAR(512),
        full_name VARCHAR(100),
        email VARCHAR(100),
        subject_assigned VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """, commit=True)

    execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        serial_no INT,
        prn VARCHAR(50) UNIQUE,
        name VARCHAR(120),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """, commit=True)

    execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        teacher_id INT,
        subject VARCHAR(120),
        date DATE,
        time TIME,
        session_type ENUM('theory','practical','tutorial'),
        status ENUM('present','absent'),
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """, commit=True)

def create_default_admin():
    r = execute("SELECT COUNT(*) as cnt FROM admins", fetch=True)
    if r and r[0]['cnt'] == 0:
        ph = utils.hash_password("admin123")
        execute("INSERT INTO admins (username, password_hash, full_name) VALUES (%s,%s,%s)",
                ("admin", ph, "Super Admin"), commit=True)
        print("Default admin created: username=admin password=admin123")
