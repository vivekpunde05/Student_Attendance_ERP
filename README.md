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

| Role    | Username | Password   |
|---------|----------|------------|
| Admin   | `admin`  | `admin123` |

> **Note:** 
> - Teachers and students must be added via the Admin panel first.
> - Teachers log in with their username and password.
> - Students log in with their **PRN** (not username).

## ✨ Features

### Admin
- ✅ Add/View/Delete Teachers & Students
- ✅ System statistics
- ✅ **Class-based filtering** (FY / SY / TY)
- ✅ Teacher-wise attendance reports with **PDF export**
- ✅ Password reset management

### Teacher
- ✅ Mark attendance (Theory / Practical / Tutorial)
- ✅ View records & summaries (%)
- ✅ Delete incorrect entries
- ✅ **Class-based filtering** when marking attendance
- ✅ **PDF attendance report** generation and download

### Student
- ✅ Personal attendance history
- ✅ Session-wise breakdown
- ✅ Overall percentage
- ✅ **Subject and session filtering**
- ✅ **Chart.js visual dashboard** for attendance analytics

### System
- ✅ Secure password reset via token (Admin / Teacher)
- ✅ Change password while logged in
- ✅ Health check endpoint for monitoring
- ✅ PBKDF2 + bcrypt password hashing
- ✅ Session-based authentication with role access control

## 🛠 Tech Stack

| Component     | Tech                   |
|---------------|------------------------|
| Backend       | Flask 3.1.2            |
| Database      | MySQL 8.0 (Aiven)      |
| ORM/Connector | mysql-connector-python |
| Auth          | PBKDF2 + bcrypt + Sessions |
| Frontend      | HTML / CSS / Jinja2 / Chart.js |
| PDF Reports   | ReportLab              |
| Deployment    | Render                 |

## 🗄 Database Schema

```sql
admins(
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  password_hash VARCHAR(512),
  full_name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  reset_token VARCHAR(64) NULL,
  reset_expires TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

teachers(
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  password_hash VARCHAR(512),
  full_name VARCHAR(100),
  email VARCHAR(100),
  subject_assigned VARCHAR(100),
  reset_token VARCHAR(64) NULL,
  reset_expires TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

students(
  id INT AUTO_INCREMENT PRIMARY KEY,
  serial_no INT,
  prn VARCHAR(50) UNIQUE,
  name VARCHAR(120),
  class_name VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

attendance(
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  teacher_id INT,
  subject VARCHAR(120),
  date DATE,
  time TIME,
  session_type ENUM('theory','practical','tutorial'),
  status ENUM('present','absent'),
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
)

password_reset_tokens(
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(100) NOT NULL,
  token VARCHAR(64) UNIQUE NOT NULL,
  user_type ENUM('admin','teacher') NOT NULL,
  user_id INT NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_token (token),
  INDEX idx_email (email)
)
```

## ☁️ Cloud Deployment (Render)

1. Push to GitHub
2. Connect repo at [render.com](https://render.com)
3. Set env vars (same as `.env`)
4. scriAuto-deploys via `render.yaml`

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| DB Connection | Run `python test_connection.py` |
| Port 5000 busy | Edit `app.py`: `port=5001` |
| SSL Error | Ensure `ssl-mode=REQUIRED` in Aiven connection |
| PDF generation error | Ensure `reportlab` is installed and `reports/` directory is writable |

**Server Logs:** Check terminal for `werkzeug` output.

## 📁 Project Structure

```
├── app.py                  # Flask app & routes
├── config.py               # Env config loader
├── connection.py           # MySQL connection pool
├── database.py             # Schema init & migrations
├── admin.py                # Admin logic
├── teacher.py              # Teacher logic
├── student.py              # Student logic
├── password_reset.py       # Password reset blueprint & logic
├── pdf_generator.py        # PDF report generation
├── utils.py                # Helpers (hashing, email, validation)
├── csv_handler.py          # CSV import/export utilities
├── templates/              # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── change_password.html
│   ├── admin/
│   ├── teacher/
│   ├── student/
│   └── password_reset/
├── static/                 # CSS, JS, assets
│   └── style.css
├── reports/                # Generated PDF reports
├── requirements.txt
├── .env                    # Secrets (gitignored)
├── test_connection.py
├── test_pdf_db.py
└── render.yaml
```

## 🔗 API Endpoints

```
Auth:
  GET/POST  /login
  GET       /logout
  GET/POST  /forgot-password
  GET/POST  /reset-password/<token>
  GET/POST  /change-password

Admin:
  GET       /admin/dashboard
  GET       /admin/teachers
  POST      /admin/teachers/add
  GET       /admin/teachers/delete/<id>
  GET       /admin/students
  POST      /admin/students/add
  GET       /admin/students/delete/<id>
  GET/POST  /admin/reports
  GET/POST  /admin/attendance-report

Teacher:
  GET       /teacher/dashboard
  GET/POST  /teacher/mark-attendance
  GET       /teacher/view-attendance
  GET       /teacher/attendance/delete/<id>
  GET       /teacher/summary
  GET/POST  /teacher/attendance-report

Student:
  GET       /student/dashboard
  GET       /student/attendance-data      # JSON for Chart.js

System:
  GET       /health                       # Health check
```

## 📈 Usage Workflow

```
Admin → Add Teacher/Student → Login Teacher → Mark Attendance → View Reports / Download PDF
Student → Login with PRN → Check Dashboard with Charts
Teacher/Admin → Forgot Password → Reset via Email Token
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
- [x] Password reset flow tested
- [x] PDF report generation tested