from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from connection import init_pool
import database
from admin import *
from teacher import *
from student import *
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production' 

# Initialize database
def setup():
    init_pool()
    database.create_tables()
    database.create_default_admin()


# Login required 
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        elif role == 'student':
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if role == 'admin':
            user = admin_login(username, password)
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))

        elif role == 'teacher':
            user = teacher_login(username, password)
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['subject'] = user['subject_assigned']
                session['role'] = 'teacher'
                return redirect(url_for('teacher_dashboard'))

        elif role == 'student':
            user = get_student_by_prn(username)
            if user:
                session['user_id'] = user['id']
                session['prn'] = user['prn']
                session['full_name'] = user['name']
                session['role'] = 'student'
                return redirect(url_for('student_dashboard'))

        flash('Invalid credentials', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Admin Routes
@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    stats = get_statistics()
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/teachers')
@login_required(role='admin')
def admin_teachers():
    teachers = list_teachers()
    return render_template('admin/teachers.html', teachers=teachers)

@app.route('/admin/teachers/add', methods=['POST'])
@login_required(role='admin')
def admin_add_teacher():
    username = request.form.get('username')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    subject = request.form.get('subject')

    add_teacher(username, password, full_name, email, subject)
    flash('Teacher added successfully', 'success')
    return redirect(url_for('admin_teachers'))

@app.route('/admin/teachers/delete/<int:teacher_id>')
@login_required(role='admin')
def admin_delete_teacher(teacher_id):
    remove_teacher(teacher_id)
    flash('Teacher deleted successfully', 'success')
    return redirect(url_for('admin_teachers'))

@app.route('/admin/students')
@login_required(role='admin')
def admin_students():
    students = list_students()
    return render_template('admin/students.html', students=students)

@app.route('/admin/students/add', methods=['POST'])
@login_required(role='admin')
def admin_add_student():
    serial_no = request.form.get('serial_no')
    prn = request.form.get('prn')
    name = request.form.get('name')

    add_student(serial_no, prn, name)
    flash('Student added successfully', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/students/delete/<int:student_id>')
@login_required(role='admin')
def admin_delete_student(student_id):
    remove_student(student_id)
    flash('Student deleted successfully', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/reports')
@login_required(role='admin')
def admin_reports():
    teachers = list_teachers()
    teacher_id = request.args.get('teacher_id', type=int)
    summary = None
    selected_teacher = None

    if teacher_id:
        summary = overall_attendance_summary(teacher_id)
        selected_teacher = next((t for t in teachers if t['id'] == teacher_id), None)

    return render_template('admin/reports.html', teachers=teachers, summary=summary, selected_teacher=selected_teacher)

# Teacher Routes
@app.route('/teacher/dashboard')
@login_required(role='teacher')
def teacher_dashboard():
    stats = get_teacher_statistics(session['user_id'])
    return render_template('teacher/dashboard.html', stats=stats)

@app.route('/teacher/mark-attendance', methods=['GET', 'POST'])
@login_required(role='teacher')
def teacher_mark_attendance():
    if request.method == 'POST':
        session_type = request.form.get('session_type')
        students = view_students()
        attendance_list = []

        for student in students:
            status = request.form.get(f'status_{student["id"]}')
            if status:
                attendance_list.append((student['id'], status))

        mark_attendance(session['user_id'], session['subject'], session_type, attendance_list)
        flash('Attendance marked successfully', 'success')
        return redirect(url_for('teacher_view_attendance'))

    students = view_students()
    return render_template('teacher/mark_attendance.html', students=students)

@app.route('/teacher/view-attendance')
@login_required(role='teacher')
def teacher_view_attendance():
    records = view_attendance(session['user_id'])
    return render_template('teacher/view_attendance.html', records=records)

@app.route('/teacher/attendance/delete/<int:att_id>')
@login_required(role='teacher')
def teacher_delete_attendance(att_id):
    delete_attendance(att_id)
    flash('Attendance record deleted', 'success')
    return redirect(url_for('teacher_view_attendance'))

@app.route('/teacher/summary')
@login_required(role='teacher')
def teacher_summary():
    summary = overall_attendance_summary(session['user_id'])
    return render_template('teacher/summary.html', summary=summary)

# Student Routes
@app.route('/student/dashboard')
@login_required(role='student')
def student_dashboard():
    records = student_view(session['prn'])
    stats = get_student_statistics(session['prn'])
    return render_template('student/dashboard.html', records=records, stats=stats)


if __name__ == '__main__':
    setup()  
    app.run(debug=True, host='0.0.0.0', port=5000)
