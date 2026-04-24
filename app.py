from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from connection import init_pool
import database
from admin import *
from teacher import *
from student import *
from functools import wraps
import os
import logging
from password_reset import password_reset_bp, create_reset_tokens_table
import pdf_generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.register_blueprint(password_reset_bp)

# Initialize database
def setup():
    try:
        init_pool()
        logger.info("Database pool initialized")
        database.create_tables()
        logger.info("Database tables created/verified")
        database.migrate_students_add_class()
        logger.info("Student class column migrated")
        create_reset_tokens_table()
        logger.info("Password reset tables created/verified")
        database.create_default_admin()
        logger.info("Default admin created/verified")
    except Exception as e:
        logger.error(f"Setup error: {e}")
        # Don't raise - allow app to start even if DB setup fails
        pass

# Run setup when module is imported (for Gunicorn)
try:
    setup()
    logger.info("Application setup completed")
except Exception as e:
    logger.error(f"Failed to setup application: {e}")


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
@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    try:
        from connection import execute
        execute("SELECT 1", fetch=True)
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

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
        try:
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
                else:
                    flash('Admin username not found. Please enter the correct username.', 'error')
                    return render_template('login.html')

            elif role == 'teacher':
                user = teacher_login(username, password)
                if user:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['full_name'] = user['full_name']
                    session['subject'] = user['subject_assigned']
                    session['role'] = 'teacher'
                    return redirect(url_for('teacher_dashboard'))
                else:
                    flash('Teacher username not found. Please enter the correct username.', 'error')
                    return render_template('login.html')

            elif role == 'student':
                user = get_student_by_prn(username)
                if user:
                    session['user_id'] = user['id']
                    session['prn'] = user['prn']
                    session['full_name'] = user['name']
                    session['role'] = 'student'
                    return redirect(url_for('student_dashboard'))
                else:
                    flash('Student PRN not found. Please enter the correct PRN.', 'error')
                    return render_template('login.html')

        except ValueError as e:
            flash(str(e), 'error')
            return render_template('login.html')
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('Database connection error. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

from utils import generate_reset_token, send_reset_email
from connection import execute
import database
from datetime import datetime, timedelta

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')

        try:
            if role == 'admin':
                user = execute("SELECT * FROM admins WHERE username = %s", (username,), fetch=True)
                if user:
                    flash('Reset link sent for admin account! (Demo - check console)', 'success')
                    token = generate_reset_token()
                    print(f"Admin {username} reset token: http://localhost:5000/reset-password/{token}")
                else:
                    flash('Username not found', 'error')

            elif role == 'teacher':
                user = execute("SELECT * FROM teachers WHERE username = %s", (username,), fetch=True)
                if user:
                    user = user[0]
                    if user.get('email') == email:
                        token = generate_reset_token()
                        expires = datetime.now() + timedelta(hours=1)
                        execute("UPDATE teachers SET reset_token = %s, reset_expires = %s WHERE id = %s", 
                               (token, expires, user['id']), commit=True)
                        if send_reset_email(email, username, token):
                            flash('Reset link sent to your email!', 'success')
                        else:
                            flash('Email sent (check console if no SMTP)', 'success')
                    else:
                        flash('Email mismatch', 'error')
                else:
                    flash('Teacher username not found. Add teacher first.', 'error')

            else:
                flash('Forgot password available for Admin/Teacher only.', 'error')

        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('forgot_password.html', role=request.form.get('role') if request.method == 'POST' else None)

# Admin Routes
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        is_valid, error = utils.validate_password_length(new_password)
        if not is_valid:
            flash(error, 'error')
            return render_template('reset_password.html', token=token)
        
        # Check token for admin
        admin = execute("SELECT * FROM admins WHERE reset_token = %s AND reset_expires > NOW()", (token,), fetch=True)
        if admin:
            admin = admin[0]
            pw_hash = utils.hash_password(new_password)
            execute("UPDATE admins SET password_hash = %s, reset_token = NULL, reset_expires = NULL WHERE id = %s", 
                   (pw_hash, admin['id']), commit=True)
            flash('Password reset successfully! Login with new password.', 'success')
            return redirect(url_for('login'))
        
        # Check token for teacher
        teacher = execute("SELECT * FROM teachers WHERE reset_token = %s AND reset_expires > NOW()", (token,), fetch=True)
        if teacher:
            teacher = teacher[0]
            pw_hash = utils.hash_password(new_password)
            execute("UPDATE teachers SET password_hash = %s, reset_token = NULL, reset_expires = NULL WHERE id = %s", 
                   (pw_hash, teacher['id']), commit=True)
            flash('Password reset successfully! Login with new password.', 'success')
            return redirect(url_for('login'))
        
        flash('Invalid or expired reset link', 'error')
        return render_template('reset_password.html', token=token)
    
    # GET: Show form
    return render_template('reset_password.html', token=token)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required()
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        role = session.get('role')
        user_id = session['user_id']

        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('change_password'))

        try:
            if role == 'admin':
                admin = execute("SELECT * FROM admins WHERE id = %s", (user_id,), fetch=True)
                if admin and utils.verify_password(admin[0]['password_hash'], current_password):
                    change_admin_password(user_id, new_password)
                    flash('Password changed successfully! Please login again.', 'success')
                    return redirect(url_for('logout'))
                else:
                    flash('Current password is incorrect', 'error')
                    return redirect(url_for('change_password'))

            elif role == 'teacher':
                teacher = execute("SELECT * FROM teachers WHERE id = %s", (user_id,), fetch=True)
                if teacher and utils.verify_password(teacher[0]['password_hash'], current_password):
                    change_teacher_password(user_id, new_password)
                    flash('Password changed successfully! Please login again.', 'success')
                    return redirect(url_for('logout'))
                else:
                    flash('Current password is incorrect', 'error')
                    return redirect(url_for('change_password'))

            else:
                flash('Password change not available for students', 'error')
                return redirect(url_for('index'))

        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('change_password'))
        except Exception as e:
            logger.error(f"Change password error: {e}")
            flash('Error changing password', 'error')
            return redirect(url_for('change_password'))

    return render_template('change_password.html')


# Admin Routes
@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    try:
        stats = get_statistics()
        return render_template('admin/dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        flash('Error loading dashboard. Please check database connection.', 'error')
        return redirect(url_for('login'))

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

    try:
        add_teacher(username, password, full_name, email, subject)
        flash('Teacher added successfully', 'success')
    except ValueError as e:
        flash(str(e), 'error')
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
    selected_class = request.args.get('class_name', 'all')
    class_filter = None if selected_class == 'all' else selected_class
    students = list_students(class_name=class_filter)
    classes = get_distinct_student_classes()
    return render_template('admin/students.html', students=students, classes=classes, selected_class=selected_class)

@app.route('/admin/students/add', methods=['POST'])
@login_required(role='admin')
def admin_add_student():
    serial_no = request.form.get('serial_no')
    prn = request.form.get('prn')
    name = request.form.get('name')
    class_name = request.form.get('class_name')

    add_student(serial_no, prn, name, class_name)
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
    selected_class = request.args.get('class_name', 'all')
    class_filter = None if selected_class == 'all' else selected_class

    if request.method == 'POST':
        session_type = request.form.get('session_type')
        date = request.form.get('date')
        # Use the same class filter that was shown in the form
        post_class = request.form.get('selected_class_name', 'all')
        class_filter_post = None if post_class == 'all' else post_class
        students = view_students(class_name=class_filter_post)
        attendance_list = []

        for student in students:
            status = request.form.get(f'status_{student["id"]}')
            if status:
                attendance_list.append((student['id'], status))

        mark_attendance(session['user_id'], session['subject'], session_type, attendance_list, date=date)
        flash('Attendance marked successfully', 'success')
        return redirect(url_for('teacher_view_attendance'))

    students = view_students(class_name=class_filter)
    classes = get_distinct_student_classes()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('teacher/mark_attendance.html', students=students, classes=classes, selected_class=selected_class, today=today)

@app.route('/teacher/view-attendance')
@login_required(role='teacher')
def teacher_view_attendance():
    session_type = request.args.get('session_type')
    records = view_attendance(session['user_id'], session_type=session_type)
    return render_template('teacher/view_attendance.html', records=records, selected_session=session_type)

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
    prn = session['prn']
    selected_subject = request.args.get('subject', 'all')
    selected_session = request.args.get('session_type', 'all')

    # Resolve filters
    subject_filter = None if selected_subject == 'all' else selected_subject
    session_filter = None if selected_session == 'all' else selected_session

    # Fetch data
    subjects = get_student_subjects(prn)
    records = get_student_attendance_filtered(prn, subject=subject_filter, session_type=session_filter)
    raw_subject_stats = get_student_statistics_by_subject(prn, subject=subject_filter)
    grand_total = raw_subject_stats.pop('__grand_total__', None) if raw_subject_stats else None
    subject_stats = raw_subject_stats if raw_subject_stats else None

    # Fallback to basic stats if no subject-level data
    basic_stats = get_student_statistics(prn) if not subject_stats else None

    return render_template(
        'student/dashboard.html',
        records=records,
        subjects=subjects,
        selected_subject=selected_subject,
        selected_session=selected_session,
        subject_stats=subject_stats,
        grand_total=grand_total,
        basic_stats=basic_stats
    )


@app.route('/student/attendance-data')
@login_required(role='student')
def student_attendance_data():
    """JSON endpoint for Chart.js graphs."""
    prn = session['prn']
    selected_subject = request.args.get('subject', 'all')
    subject_filter = None if selected_subject == 'all' else selected_subject

    stats = get_student_statistics_by_subject(prn, subject=subject_filter)
    grand_total = stats.pop('__grand_total__', None) if stats else None

    # Prepare chart data
    labels = list(stats.keys())
    overall_pcts = [stats[s]['overall']['percentage'] for s in labels]
    theory_pcts = [stats[s]['theory']['percentage'] for s in labels]
    practical_pcts = [stats[s]['practical']['percentage'] for s in labels]
    tutorial_pcts = [stats[s]['tutorial']['percentage'] for s in labels]

    present_counts = [stats[s]['overall']['present'] for s in labels]
    absent_counts = [stats[s]['overall']['total'] - stats[s]['overall']['present'] for s in labels]

    return jsonify({
        'labels': labels,
        'overall_percentages': overall_pcts,
        'theory_percentages': theory_pcts,
        'practical_percentages': practical_pcts,
        'tutorial_percentages': tutorial_pcts,
        'present_counts': present_counts,
        'absent_counts': absent_counts,
        'grand_total': grand_total
    })


# Helper: compute summary statistics for report preview
def _compute_report_stats(summary):
    total_students = len(summary)
    total_pct = sum(d.get("overall", {}).get("percentage", 0) for d in summary.values())
    avg_percentage = round(total_pct / total_students, 2) if total_students > 0 else 0
    low_count = sum(1 for d in summary.values() if d.get("overall", {}).get("percentage", 0) < 50)
    return total_students, avg_percentage, low_count


# Attendance Report Routes
@app.route('/teacher/attendance-report', methods=['GET', 'POST'])
@login_required(role='teacher')
def teacher_attendance_report():
    teacher_id = session['user_id']
    teacher_name = session.get('full_name', 'Teacher')
    subject = session.get('subject', 'N/A')

    if request.method == 'POST':
        summary = overall_attendance_summary(teacher_id)
        if not summary:
            flash('No attendance data available to generate report.', 'error')
            return redirect(url_for('teacher_attendance_report'))

        os.makedirs('reports', exist_ok=True)
        filename = f"attendance_report_{teacher_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join('reports', filename)

        try:
            pdf_generator.generate_attendance_pdf(summary, teacher_name, subject, output_path)
            return send_file(output_path, as_attachment=True, download_name=filename)
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            flash('Error generating PDF. Please try again.', 'error')
            return redirect(url_for('teacher_attendance_report'))

    summary = overall_attendance_summary(teacher_id)
    total_students, avg_percentage, low_count = _compute_report_stats(summary)
    return render_template(
        'teacher/attendance_report.html',
        summary=summary,
        total_students=total_students,
        avg_percentage=avg_percentage,
        low_count=low_count,
    )


@app.route('/admin/attendance-report', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_attendance_report():
    teachers = list_teachers()

    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id', type=int)
        if not teacher_id:
            flash('Please select a teacher.', 'error')
            return redirect(url_for('admin_attendance_report'))

        summary = overall_attendance_summary(teacher_id)
        if not summary:
            flash('No attendance data available for the selected teacher.', 'error')
            return redirect(url_for('admin_attendance_report'))

        teacher = get_teacher_by_id(teacher_id)
        teacher_name = teacher['full_name'] if teacher else 'Teacher'
        subject = teacher['subject_assigned'] if teacher else 'N/A'

        os.makedirs('reports', exist_ok=True)
        filename = f"attendance_report_{teacher_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join('reports', filename)

        try:
            pdf_generator.generate_attendance_pdf(summary, teacher_name, subject, output_path)
            return send_file(output_path, as_attachment=True, download_name=filename)
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            flash('Error generating PDF. Please try again.', 'error')
            return redirect(url_for('admin_attendance_report'))

    teacher_id = request.args.get('teacher_id', type=int)
    summary = None
    selected_teacher = None
    total_students = avg_percentage = low_count = 0

    if teacher_id:
        summary = overall_attendance_summary(teacher_id)
        selected_teacher = get_teacher_by_id(teacher_id)
        total_students, avg_percentage, low_count = _compute_report_stats(summary)

    return render_template(
        'admin/attendance_report.html',
        teachers=teachers,
        summary=summary,
        selected_teacher=selected_teacher,
        total_students=total_students,
        avg_percentage=avg_percentage,
        low_count=low_count,
    )


if __name__ == '__main__':
    import os
    try:
        setup()
        print("Database setup completed successfully")
    except Exception as e:
        print(f"Warning during setup: {e}")
        # Continue anyway - tables might already exist
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
