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


def get_student_subjects(prn):
    """Return distinct subjects for a student ordered alphabetically."""
    q = """
        SELECT DISTINCT a.subject
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE s.prn = %s
        ORDER BY a.subject
    """
    rows = execute(q, (prn,), fetch=True)
    return [r['subject'] for r in rows if r['subject']]


def get_student_statistics_by_subject(prn, subject=None):
    """
    Return attendance statistics grouped by subject.
    If subject is provided, returns stats for only that subject.
    Structure: {
        'subject_name': {
            'theory': {'total': x, 'present': y, 'percentage': z},
            'practical': {...},
            'tutorial': {...},
            'overall': {...}
        },
        ...
    }
    Also returns a grand_total key with aggregated stats across all subjects.
    """
    student = get_student_by_prn(prn)
    if not student:
        return None

    if subject:
        q = """
            SELECT a.subject, a.session_type, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE s.prn = %s AND a.subject = %s
        """
        params = (prn, subject)
    else:
        q = """
            SELECT a.subject, a.session_type, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE s.prn = %s
        """
        params = (prn,)

    records = execute(q, params, fetch=True)

    stats = {}
    grand_total = {
        'theory': {'total': 0, 'present': 0, 'percentage': 0},
        'practical': {'total': 0, 'present': 0, 'percentage': 0},
        'tutorial': {'total': 0, 'present': 0, 'percentage': 0},
        'overall': {'total': 0, 'present': 0, 'percentage': 0}
    }

    for record in records:
        subj = record['subject'] or 'Unknown'
        stype = record['session_type']
        status = record['status']

        if subj not in stats:
            stats[subj] = {
                'theory': {'total': 0, 'present': 0, 'percentage': 0},
                'practical': {'total': 0, 'present': 0, 'percentage': 0},
                'tutorial': {'total': 0, 'present': 0, 'percentage': 0},
                'overall': {'total': 0, 'present': 0, 'percentage': 0}
            }

        stats[subj][stype]['total'] += 1
        stats[subj]['overall']['total'] += 1
        grand_total[stype]['total'] += 1
        grand_total['overall']['total'] += 1

        if status == 'present':
            stats[subj][stype]['present'] += 1
            stats[subj]['overall']['present'] += 1
            grand_total[stype]['present'] += 1
            grand_total['overall']['present'] += 1

    # Calculate percentages
    for subj in stats:
        for key in stats[subj]:
            if stats[subj][key]['total'] > 0:
                stats[subj][key]['percentage'] = round(
                    (stats[subj][key]['present'] / stats[subj][key]['total']) * 100, 2
                )

    for key in grand_total:
        if grand_total[key]['total'] > 0:
            grand_total[key]['percentage'] = round(
                (grand_total[key]['present'] / grand_total[key]['total']) * 100, 2
            )

    stats['__grand_total__'] = grand_total
    return stats


def get_student_attendance_filtered(prn, subject=None, session_type=None):
    """
    Return attendance records filtered by subject and/or session_type.
    """
    base_q = """
        SELECT a.id, s.serial_no, s.prn, s.name, a.subject, a.date, a.time, a.session_type, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE s.prn = %s
    """
    conditions = []
    params = [prn]

    if subject:
        conditions.append("a.subject = %s")
        params.append(subject)

    if session_type:
        conditions.append("a.session_type = %s")
        params.append(session_type)

    if conditions:
        base_q += " AND " + " AND ".join(conditions)

    base_q += " ORDER BY a.date DESC, a.time DESC"

    return execute(base_q, tuple(params), fetch=True)

