# Student Attendance ERP System

A comprehensive web-based attendance management system built with Flask and MySQL.

## Features

### Admin Dashboard
- Manage teachers (Add, View, Delete)
- Manage students (Add, View, Delete)
- View system statistics
- Generate attendance reports

### Teacher Dashboard
- Mark attendance (Theory/Practical/Tutorial)
- View attendance records
- Student-wise attendance summary
- Update/Delete attendance records

### Student Dashboard
- View personal attendance history
- Session-wise attendance breakdown
- Overall attendance percentage

## Prerequisites

- Python 3.8 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

## Installation Steps

### 1. Install MySQL Server

**Windows:**
- Download from: https://dev.mysql.com/downloads/mysql/
- Run the installer and follow the setup wizard
- Remember the root password you set

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### 2. Create Database

Open MySQL command line or MySQL Workbench and run:

```sql
CREATE DATABASE attendance;
```

Or use command line:
```bash
mysql -u root -p
# Enter your password
CREATE DATABASE attendance;
exit;
```

### 3. Setup Project

1. Extract the ZIP file to your desired location
2. Open the folder in VS Code
3. Open Terminal in VS Code (Ctrl + ` or View > Terminal)

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Database

Edit `config.py` and update your MySQL credentials:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD", 
    "database": "attendance",
    "port": 3306,
}
```

### 6. Run the Application

```bash
python app.py
```

The application will:
- Create all necessary database tables
- Create a default admin account
- Start the Flask development server

### 7. Access the Application

Open your web browser and go to:
```
http://localhost:5000
```

## Default Login Credentials

**Admin:**
- Username: `admin`
- Password: `admin123`

**Note:** After first login, please add teachers and students through the admin panel.

## Project Structure

```
attendance-erp/
├── app.py                 # Main Flask application
├── config.py             # Database configuration
├── connection.py         # Database connection pool
├── database.py           # Database schema and initialization
├── utils.py              # Utility functions (password hashing, etc.)
├── admin.py              # Admin module functions
├── teacher.py            # Teacher module functions
├── student.py            # Student module functions
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/           # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── teachers.html
│   │   ├── students.html
│   │   └── reports.html
│   ├── teacher/
│   │   ├── dashboard.html
│   │   ├── mark_attendance.html
│   │   ├── view_attendance.html
│   │   └── summary.html
│   └── student/
│       └── dashboard.html
└── static/              # CSS, JS, images
    └── style.css

```

## Usage Guide

### Admin Tasks

1. **Add Teacher:**
   - Login as admin
   - Go to "Teachers" section
   - Click "Add Teacher"
   - Fill in the details and submit

2. **Add Student:**
   - Go to "Students" section
   - Click "Add Student"
   - Enter Serial No, PRN, and Name

3. **View Reports:**
   - Go to "Reports" section
   - Select a teacher
   - View attendance summary for all students

### Teacher Tasks

1. **Mark Attendance:**
   - Login with teacher credentials
   - Go to "Mark Attendance"
   - Select session type (Theory/Practical/Tutorial)
   - Mark Present/Absent for each student
   - Submit

2. **View Records:**
   - Go to "View Attendance"
   - See all attendance records
   - Delete records if needed

3. **Student Summary:**
   - Go to "Summary"
   - View detailed attendance breakdown for each student

### Student Tasks

1. **View Attendance:**
   - Login with PRN number
   - View attendance history
   - Check session-wise percentages

## Troubleshooting

### Database Connection Error

If you see "Can't connect to MySQL server":
1. Make sure MySQL service is running
2. Check credentials in `config.py`
3. Verify database 'attendance' exists

### Module Not Found Error

```bash
pip install --upgrade -r requirements.txt
```

### Port Already in Use

Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  
```

## Security Notes

- Change the `app.secret_key` in `app.py` before deployment
- Use strong passwords for admin accounts
- Don't deploy with `debug=True` in production
- Use environment variables for sensitive configuration

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review MySQL and Flask documentation
3. Ensure all dependencies are installed correctly

## License

This project is for educational purposes.
