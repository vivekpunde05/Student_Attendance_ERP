# Student Attendance ERP System

A comprehensive web-based attendance management system built with **Flask** and **MySQL**. Supports local development and cloud deployment (Render + Aiven MySQL).

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://www.mysql.com/)

**Last Updated:** Current - Verified working locally with Aiven MySQL

## 🚀 Quick Start (Local)

1. **Clone & Setup**
   ```bash
   git clone <repo-url>
   cd Student_Attendance_ERP
   ```

2. **Virtual Environment**
   ```powershell
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database** (Aiven MySQL or local)
   Create `.env`:
   ```env

 DB_HOST=your-host
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-db-name
DB_PORT=your-port
SECRET_KEY=your-secret-key
   ```

5. **Test Connection**
   ```bash
   python test_connection.py
   ```

6. **Run Server**
   ```bash
   python app.py
   ```
   **URL:** http://localhost:5000

## 👤 Default Login

| Role   | Username | Password    |
|--------|----------|-------------|
| Admin  | `admin`  | `admin123`  |

> **Note:** Add teachers/students via Admin panel first.

## ✨ Features

### Admin
- ✅ Add/View/Delete Teachers & Students
- ✅ System statistics
- ✅ Teacher-wise attendance reports

### Teacher
- ✅ Mark attendance (Theory/Practical/Tutorial)
- ✅ View records & summaries (%)
- ✅ Delete incorrect entries

### Student
- ✅ Personal attendance history
- ✅ Session-wise breakdown
- ✅ Overall percentage

## 🛠 Tech Stack

| Component     | Tech              |
|---------------|-------------------|
| Backend       | Flask 3.1.2      |
| Database      | MySQL 8.0 (Aiven)|
| ORM           | mysql-connector  |
| Auth          | PBKDF2 + Sessions|
| Frontend      | HTML/CSS/Jinja2  |
| Deployment    | Render           |

## 🗄 Database Schema

```sql
admins(id, username, password_hash, full_name, created_at)
teachers(id, username, password_hash, full_name, email, subject_assigned, created_at)
students(id, serial_no, prn, name, created_at)
attendance(id, student_id, teacher_id, subject, date, time, session_type, status, recorded_at)
```

## ☁️ Cloud Deployment (Render)

1. Push to GitHub
2. Connect repo at [render.com](https://render.com)
3. Set env vars (same as `.env`)
4. Auto-deploys via `render.yaml`

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| DB Connection | Run `python test_connection.py` |
| Port 5000 busy | Edit `app.py`: `port=5001` |
| SSL Error | Ensure `ssl-mode=REQUIRED` in Aiven connection |

**Server Logs:** Check terminal for `werkzeug` output.

## 📁 Project Structure

```
├── app.py           # Flask app
├── config.py        # Env config
├── connection.py    # MySQL pool
├── database.py      # Schema init
├── admin.py         # Admin logic
├── teacher.py       # Teacher logic
├── student.py       # Student logic
├── utils.py         # Helpers
├── templates/       # HTML
├── static/          # CSS
├── requirements.txt
├── .env            # Secrets (gitignore)
└── test_connection.py
```

## 🔗 API Endpoints

```
Auth: /login, /logout
Admin: /admin/dashboard, /admin/teachers, /admin/students, /admin/reports
Teacher: /teacher/* (mark-attendance, view-attendance, summary)
Student: /student/dashboard
Health: /health
```

## 📈 Usage Workflow

```
Admin → Add Teacher/Student → Login Teacher → Mark Attendance → View Reports
Student → Login PRN → Check Dashboard
```

## 🤝 Contributing

1. Fork → Branch → Commit → PR
2. Follow PEP8
3. Update tests
4. `git commit -m "feat: description"`

## 📄 License

Educational use.

## 👨‍💻 Author

**Vivek Punde**  
[GitHub](https://github.com/vivekpunde05)

## ✅ Verified Setup

- [x] Python 3.13 + venv
- [x] Dependencies installed
- [x] Aiven MySQL connected
- [x] App running @ localhost:5000
- [x] Default admin login works

