from connection import execute
import utils

def admin_login(username, password):
    r = execute("SELECT * FROM admins WHERE username = %s", (username,), fetch=True)
    if not r:
        return None
    admin = r[0]
    if utils.verify_password(admin['password_hash'], password):
        return admin
    return None

def add_teacher(username, password, full_name, email, subject):
    pw_hash = utils.hash_password(password)
    execute("INSERT INTO teachers (username,password_hash,full_name,email,subject_assigned) VALUES (%s,%s,%s,%s,%s)",
            (username, pw_hash, full_name, email, subject), commit=True)

def list_teachers():
    return execute("SELECT * FROM teachers", fetch=True)

def remove_teacher(teacher_id):
    execute("DELETE FROM teachers WHERE id=%s", (teacher_id,), commit=True)

def add_student(serial_no, prn, name):
    execute("INSERT INTO students (serial_no,prn,name) VALUES (%s,%s,%s)",
            (serial_no, prn, name), commit=True)

def update_student(student_id, name=None):
    if name:
        execute("UPDATE students SET name=%s WHERE id=%s", (name, student_id), commit=True)

def list_students():
    return execute("SELECT * FROM students ORDER BY serial_no", fetch=True)

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
