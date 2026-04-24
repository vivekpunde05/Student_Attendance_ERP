# TODO: Add Class Filter to Admin Reports

## Task
In the admin session, when the user goes to Reports, add options to select **Teacher** and **Class** (e.g., TY AIDS, FY AIDS, etc.).

## Plan

### Step 1: Update `teacher.py` backend functions ✅
- Modify `attendance_summary_by_type(teacher_id, class_name=None)` to accept optional `class_name` and filter by it.
- Modify `overall_attendance_summary(teacher_id, class_name=None)` to pass through `class_name`.

### Step 2: Update `app.py` admin report routes ✅
- Update `/admin/reports` route to:
  - Read `class_name` from query params
  - Fetch distinct classes via `get_distinct_student_classes()`
  - Pass `classes` and `selected_class` to template
  - Call `overall_attendance_summary(teacher_id, class_name)` when generating summary
- Update `/admin/attendance-report` GET route with same class handling for preview
- Update `/admin/attendance-report` POST route to read `class_name` from form for PDF generation

### Step 3: Update `templates/admin/reports.html` ✅
- Add class dropdown `<select name="class_name">` with "All Classes" option and dynamic class names
- Pre-select currently chosen class
- Show selected class in report header

### Step 4: Update `templates/admin/attendance_report.html` ✅
- Add class dropdown inside GET form
- Pre-select currently chosen class
- Show selected class in preview header
- Include `class_name` as hidden input in POST PDF form

## Files Edited
- `teacher.py`
- `app.py`
- `templates/admin/reports.html`
- `templates/admin/attendance_report.html`

