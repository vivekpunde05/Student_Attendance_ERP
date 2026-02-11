# main.py
import getpass
from connection import init_pool
import database
from admin import *
from teacher import *
from student import *


def setup():
    init_pool()
    database.create_tables()
    database.create_default_admin()

def admin_menu(admin):
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Add Teacher")
        print("2. List Teachers")
        print("3. Add Student")
        print("4. Update Student")
        print("5. List Students")
        print("6. Remove Teacher")
        print("7. Remove Student")
        print("8. View Attendance Summary (Teacher-wise)")
        print("0. Logout")

        ch = input("Choice: ")

        if ch == '1':
            u = input("Username: ")
            p = getpass.getpass("Password: ")
            n = input("Full name: ")
            e = input("Email: ")
            s = input("Subject assigned: ")
            add_teacher(u, p, n, e, s)
            print("Teacher added.")

        elif ch == '2':
            for t in list_teachers():
                print(t)

        elif ch == '3':
            s_no = int(input("Serial no: "))
            prn = input("PRN: ")
            name = input("Name: ")
            add_student(s_no, prn, name)
            print("Student added.")

        elif ch == '4':
            sid = int(input("Student ID to update: "))
            name = input("New name (blank to skip): ") or None
            update_student(sid, name)
            print("Student updated.")

        elif ch == '5':
            for s in list_students():
                print(s)

        elif ch == '6':
            tid = int(input("Enter teacher ID to remove: "))
            remove_teacher(tid)
            print("Teacher removed.")

        elif ch == '7':
            sid = int(input("Enter student ID to remove: "))
            remove_student(sid)
            print("Student removed.")

        elif ch == '8':
            tid = int(input("Enter Teacher ID: "))
            summary = overall_attendance_summary(tid)

            print("\n--- Attendance Summary ---")
            for sid, data in summary.items():
                print(f"\nStudent: {data['serial_no']} - {data['name']} (PRN:{data['prn']})")
                print(f"  Theory: {data['theory']['attended']}/{data['theory']['total']} ({data['theory']['percentage']}%)")
                print(f"  Practical: {data['practical']['attended']}/{data['practical']['total']} ({data['practical']['percentage']}%)")
                print(f"  Tutorial: {data['tutorial']['attended']}/{data['tutorial']['total']} ({data['tutorial']['percentage']}%)")
                print(f"  OVERALL: {data['overall']['attended']}/{data['overall']['total']} ({data['overall']['percentage']}%)")

        elif ch == '0':
            break

def teacher_menu(teacher):
    tid = teacher['id']
    subject = teacher['subject_assigned']

    while True:
        print(f"\n--- TEACHER MENU ({teacher['username']}) ---")
        print("1. View Students")
        print("2. Mark Attendance")
        print("3. View Attendance")
        print("4. Update Attendance")
        print("5. Delete Attendance")
        print("6. Attendance Summary")
        print("0. Logout")

        ch = input("Choice: ")

        if ch == '1':
            for s in view_students():
                print(s)

        elif ch == '2':
            stype = input("Session type (Theory/Practical/Tutorial): ").strip().lower()
            if stype not in ["theory", "practical", "tutorial"]:
                print("Invalid type! Using 'theory'.")
                stype = "theory"

            students = view_students()
            print("\nMark P/A for each student:")
            att = []

            for s in students:
                ans = input(f"{s['serial_no']} - {s['name']} (PRN:{s['prn']}): ")
                status = 'present' if ans.lower().startswith('p') else 'absent'
                att.append((s['id'], status))

            mark_attendance(tid, subject, stype, att)
            print("Attendance marked successfully.")

        elif ch == '3':
            for r in view_attendance(tid):
                print(r)

        elif ch == '4':
            att_id = int(input("Enter Attendance ID to update: "))
            new_status = input("New status (present/absent): ").lower()
            update_attendance(att_id, new_status)
            print("Attendance updated.")

        elif ch == '5':
            att_id = int(input("Enter Attendance ID to delete: "))
            delete_attendance(att_id)
            print("Attendance deleted.")

        elif ch == '6':
            summary = overall_attendance_summary(tid)
            print("\n--- Attendance Summary ---")
            for sid, data in summary.items():
                print(f"\nStudent: {data['serial_no']} - {data['name']} (PRN:{data['prn']})")
                print(f"  Theory: {data['theory']['attended']}/{data['theory']['total']} ({data['theory']['percentage']}%)")
                print(f"  Practical: {data['practical']['attended']}/{data['practical']['total']} ({data['practical']['percentage']}%)")
                print(f"  Tutorial: {data['tutorial']['attended']}/{data['tutorial']['total']} ({data['tutorial']['percentage']}%)")
                print(f"  OVERALL: {data['overall']['attended']}/{data['overall']['total']} ({data['overall']['percentage']}%)")

        elif ch == '0':
            break


def student_menu():
    prn = input("Enter your PRN: ")
    rows = student_view(prn)

    if not rows:
        print("No attendance records found.")
    else:
        for r in rows:
            print(r)


def run():
    setup()

    while True:
        print("\n--- Attendance ERP ---")
        print("1. Admin Login")
        print("2. Teacher Login")
        print("3. Student View")
        print("0. Exit")

        ch = input("Choice: ")

        if ch == '1':
            u = input("Username: ")
            p = getpass.getpass("Password: ")
            admin = admin_login(u, p)
            if admin:
                admin_menu(admin)
            else:
                print("Invalid credentials.")

        elif ch == '2':
            u = input("Username: ")
            p = getpass.getpass("Password: ")
            teacher = teacher_login(u, p)
            if teacher:
                teacher_menu(teacher)
            else:
                print("Invalid login.")

        elif ch == '3':
            student_menu()

        elif ch == '0':
            break


if __name__ == '__main__':
    run()
