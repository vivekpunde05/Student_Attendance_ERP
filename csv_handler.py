#csv_handler.py
import csv
from teacher import view_attendance

def save_attendance_for_month(teacher_id: int, year: int, month: int, out_path: str):
    
    from teacher import export_by_month
    export_by_month(teacher_id, year, month, out_path)

def save_attendance_for_year(teacher_id: int, year: int, out_path: str):
    from teacher import export_by_year
    export_by_year(teacher_id, year, out_path)
