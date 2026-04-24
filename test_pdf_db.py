import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize DB connection
from connection import init_pool, execute
import database
from teacher import overall_attendance_summary, get_teacher_by_id
from pdf_generator import generate_attendance_pdf

init_pool()
database.create_tables()

# Get all teachers
teachers = execute("SELECT * FROM teachers", fetch=True)
print(f"Found {len(teachers)} teacher(s)")

for teacher in teachers:
    tid = teacher['id']
    tname = teacher['full_name']
    subject = teacher['subject_assigned']
    print(f"\n--- Teacher: {tname} (ID: {tid}, Subject: {subject}) ---")

    summary = overall_attendance_summary(tid)
    print(f"Summary has {len(summary)} student(s)")

    if not summary:
        print("No attendance data, skipping PDF test.")
        continue

    # Print first student data structure
    first_sid = list(summary.keys())[0]
    print(f"First student data: {summary[first_sid]}")

    try:
        os.makedirs('reports', exist_ok=True)
        output_path = f'reports/test_db_teacher_{tid}.pdf'
        generate_attendance_pdf(summary, tname, subject, output_path)
        print(f"SUCCESS: PDF generated at {output_path}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()