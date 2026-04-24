from connection import execute
import utils

def admin_login(username, password):
    r = execute("SELECT * FROM admins WHERE username = %s", (username,), fetch=True)
    if not r:
        return None
    admin = r[0]
    if admin.get('password_hash') and utils.verify_password(admin['password_hash'], password):
        return admin
    raise ValueError("Incorrect password. Please enter the correct password.")

def add_teacher(username, password, full_name, email, subject):
    is_valid, error = utils.validate_password_length(password)
    if not is_valid:
        raise ValueError(f"Invalid password: {error}")
    pw_hash = utils.hash_password(password)
    execute("INSERT INTO teachers (username,password_hash,full_name,email,subject_assigned) VALUES (%s,%s,%s,%s,%s)",
            (username, pw_hash, full_name, email, subject), commit=True)

def list_teachers():
    return execute("SELECT * FROM teachers", fetch=True)

def remove_teacher(teacher_id):
    execute("DELETE FROM teachers WHERE id=%s", (teacher_id,), commit=True)

def change_admin_password(admin_id: int, new_password: str):
    """Allow admin to change their own password"""
    is_valid, error = utils.validate_password_length(new_password)
    if not is_valid:
        raise ValueError(error)
    pw_hash = utils.hash_password(new_password)
    execute("UPDATE admins SET password_hash = %s WHERE id = %s", (pw_hash, admin_id), commit=True)

def add_student(serial_no, prn, name, class_name=None):
    execute("INSERT INTO students (serial_no,prn,name,class_name) VALUES (%s,%s,%s,%s)",
            (serial_no, prn, name, class_name), commit=True)

def update_student(student_id, name=None):
    if name:
        execute("UPDATE students SET name=%s WHERE id=%s", (name, student_id), commit=True)

def list_students(class_name=None):
    if class_name:
        return execute("SELECT * FROM students WHERE class_name = %s ORDER BY serial_no", (class_name,), fetch=True)
    return execute("SELECT * FROM students ORDER BY serial_no", fetch=True)

def get_distinct_student_classes():
    rows = execute("SELECT DISTINCT class_name FROM students WHERE class_name IS NOT NULL AND class_name != '' ORDER BY class_name", fetch=True)
    return [r['class_name'] for r in rows]

def remove_student(student_id):
    execute("DELETE FROM students WHERE id=%s", (student_id,), commit=True)

def get_statistics():
    teachers = execute("SELECT COUNT(*) as count FROM teachers", fetch=True)
    students = execute("SELECT COUNT(*) as count FROM students", fetch=True)
    attendance = execute("SELECT COUNT(*) as count FROM attendance", fetch=True)

    present_count = execute("SELECT COUNT(*) as count FROM attendance WHERE status='present'", fetch=True)
    total_count = attendance[0]['count'] if attendance else 0
    avg_attendance = round((present_count[0]['count'] / total_count * 100), 2) if total_count > 0 else 0

    return {
        'teachers': teachers[0]['count'] if teachers else 0,
        'students': students[0]['count'] if students else 0,
        'attendance': total_count,
        'avg_attendance': avg_attendance
    }
