from connection import execute

def student_view(prn):
    q = """
        SELECT a.id, s.serial_no, s.prn, s.name, a.subject, a.date, a.time, a.session_type, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE s.prn = %s
        ORDER BY a.date DESC, a.time DESC
    """
    return execute(q, (prn,), fetch=True)

def get_student_by_prn(prn):
    result = execute("SELECT * FROM students WHERE prn = %s", (prn,), fetch=True)
    return result[0] if result else None

def get_student_statistics(prn):
    student = get_student_by_prn(prn)
    if not student:
        return None

    records = execute(
        "SELECT session_type, status FROM attendance a JOIN students s ON a.student_id = s.id WHERE s.prn = %s",
        (prn,), fetch=True
    )

    stats = {
        'theory': {'total': 0, 'present': 0, 'percentage': 0},
        'practical': {'total': 0, 'present': 0, 'percentage': 0},
        'tutorial': {'total': 0, 'present': 0, 'percentage': 0},
        'overall': {'total': 0, 'present': 0, 'percentage': 0}
    }

    for record in records:
        session = record['session_type']
        stats[session]['total'] += 1
        stats['overall']['total'] += 1
        if record['status'] == 'present':
            stats[session]['present'] += 1
            stats['overall']['present'] += 1

    for key in stats:
        if stats[key]['total'] > 0:
            stats[key]['percentage'] = round((stats[key]['present'] / stats[key]['total']) * 100, 2)

    return stats
