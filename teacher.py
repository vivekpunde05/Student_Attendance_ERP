from connection import execute
import utils
from utils import *

def teacher_login(username, password):
    r = execute("SELECT * FROM teachers WHERE username=%s", (username,), fetch=True)
    if not r:
        return None
    teacher = r[0]
    if utils.verify_password(teacher['password_hash'], password):
        return teacher
    return None

def view_students():
    return execute("SELECT * FROM students ORDER BY serial_no", fetch=True)

def mark_attendance(teacher_id, subject, session_type, attendance_list):
    date = now_date_str()
    time = now_time_str()
    sql = """INSERT INTO attendance (student_id, teacher_id, subject, date, time, session_type, status)
             VALUES (%s,%s,%s,%s,%s,%s,%s)"""
    params = [(sid, teacher_id, subject, date, time, session_type, status) for sid, status in attendance_list]
    execute(sql, params, many=True, commit=True)

def view_attendance(teacher_id):
    q = """SELECT a.id, s.serial_no, s.prn, s.name, a.subject, a.date, a.time, a.session_type, a.status
           FROM attendance a
           JOIN students s ON a.student_id = s.id
           WHERE a.teacher_id = %s
           ORDER BY a.date DESC, a.time DESC"""
    return execute(q, (teacher_id,), fetch=True)

def update_attendance(att_id, new_status):
    execute("UPDATE attendance SET status=%s WHERE id=%s", (new_status, att_id), commit=True)

def delete_attendance(att_id):
    execute("DELETE FROM attendance WHERE id=%s", (att_id,), commit=True)

def attendance_summary_by_type(teacher_id):
    query = """
        SELECT 
            s.id AS student_id,
            s.serial_no,
            s.prn,
            s.name,
            a.session_type,
            COUNT(*) AS total_lectures,
            SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) AS attended
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.teacher_id = %s
        GROUP BY s.id, a.session_type
        ORDER BY s.serial_no
    """
    rows = execute(query, (teacher_id,), fetch=True)

    summary = {}
    for r in rows:
        sid = r["student_id"]
        stype = r["session_type"].lower()

        if sid not in summary:
            summary[sid] = {
                "serial_no": r["serial_no"],
                "prn": r["prn"],
                "name": r["name"],
                "theory": {"attended": 0, "total": 0, "percentage": 0},
                "practical": {"attended": 0, "total": 0, "percentage": 0},
                "tutorial": {"attended": 0, "total": 0, "percentage": 0},
            }

        summary[sid][stype]["attended"] = r["attended"]
        summary[sid][stype]["total"] = r["total_lectures"]
        summary[sid][stype]["percentage"] = (
            round((r["attended"] / r["total_lectures"]) * 100, 2) if r["total_lectures"] > 0 else 0
        )
    return summary

def overall_attendance_summary(teacher_id):
    summary = attendance_summary_by_type(teacher_id)
    for sid, data in summary.items():
        total_lectures = data["theory"]["total"] + data["practical"]["total"] + data["tutorial"]["total"]
        attended = data["theory"]["attended"] + data["practical"]["attended"] + data["tutorial"]["attended"]
        percentage = round((attended / total_lectures) * 100, 2) if total_lectures > 0 else 0
        data["overall"] = {
            "attended": attended,
            "total": total_lectures,
            "percentage": percentage
        }
    return summary

def get_teacher_statistics(teacher_id):
    students = execute("SELECT COUNT(*) as count FROM students", fetch=True)

    unique_dates = execute(
        "SELECT COUNT(DISTINCT date) as count FROM attendance WHERE teacher_id = %s",
        (teacher_id,), fetch=True
    )

    attendance_records = execute(
        "SELECT COUNT(*) as total, SUM(CASE WHEN status='present' THEN 1 ELSE 0 END) as present FROM attendance WHERE teacher_id = %s",
        (teacher_id,), fetch=True
    )

    total = attendance_records[0]['total'] if attendance_records else 0
    present = attendance_records[0]['present'] if attendance_records else 0
    avg_attendance = round((present / total * 100), 2) if total > 0 else 0

    return {
        'students': students[0]['count'] if students else 0,
        'classes': unique_dates[0]['count'] if unique_dates else 0,
        'avg_attendance': avg_attendance
    }