# Security Enhancement TODO - Progress Tracker

## Plan Overview
✅ **Phase 1**: Password validation (8+ chars)  
✅ **Phase 2**: Complete Password Reset System v2  

**Current Progress: 18/18 steps complete** (ALL ✅)

---

### Phase 1: Password Validation ✅
1. ✅ Read `utils.py` & `config.py`  
2. ✅ Add `validate_password_length()` to `utils.py`  
3. ✅ Update `admin.py`: `add_teacher()` validation  
4. ✅ Update `admin.py`: `admin_login()` validation  
5. ✅ Update `teacher.py`: `teacher_login()` validation  
6. ✅ Update `app.py`: `admin_add_teacher()` error handling  
7. ✅ Client-side JS validation + HTML5 minlength on admin/teachers.html

### Phase 2: Complete Password Reset System ✅
8. ✅ Created `password_reset.py` module with full system  
9. ✅ Database table: `password_reset_tokens`  
10. ✅ Email sending via SMTP with HTML/text  
11. ✅ Route: `/forgot-password-v2` (GET/POST)  
12. ✅ Route: `/reset-password-v2` (GET/POST)  
13. ✅ Template: `password_reset/request_reset.html`  
14. ✅ Template: `password_reset/do_reset.html`  
15. ✅ Template: `password_reset/success.html`  
16. ✅ Updated `login.html` with forgot password links  
17. ✅ Migration: `migrate_admin_email_v2.py`  
18. ✅ Requirements: `bcrypt==4.2.0` added

---

## Features Implemented

### 1. Password Validation (8+ characters)
- **Server-side**: `utils.validate_password_length()` checks all passwords
- **Login rejection**: Short passwords silently rejected (security best practice)
- **Teacher creation**: Flash error shown if password < 8 chars
- **Client-side**: HTML5 `minlength="8"` + JS real-time validation

### 2. Password Reset v2 (Complete System)
| Feature | Implementation |
|---------|---------------|
| Token Generation | `secrets` module (cryptographically secure) |
| Token Storage | `password_reset_tokens` table with 30-min expiry |
| Token Validation | Check expiry + `used=FALSE` |
| Single-Use | Token marked `used=TRUE` after reset |
| Password Hashing | `bcrypt` with 12 rounds (adaptive, salt auto) |
| Email Sending | SMTP with HTML + plain text templates |
| Error Handling | Generic messages (no email enumeration) |
| Input Validation | 8-char minimum, matching confirmation |

### 3. Files Created/Modified
| File | Status | Purpose |
|------|--------|---------|
| `password_reset.py` | NEW | Complete reset system module |
| `utils.py` | MODIFIED | `validate_password_length()` |
| `admin.py` | MODIFIED | Password validation on login/add |
| `teacher.py` | MODIFIED | Password validation on login |
| `app.py` | MODIFIED | Blueprint registration, table init |
| `database.py` | MODIFIED | `email` column, `password_reset_tokens` table |
| `requirements.txt` | MODIFIED | Added `bcrypt==4.2.0` |
| `templates/password_reset/*.html` | NEW | 3 templates for reset flow |
| `templates/login.html` | MODIFIED | Added forgot password links |
| `templates/admin/teachers.html` | MODIFIED | JS validation hints |
| `migrate_admin_email_v2.py` | NEW | Admin email migration |

---

## How to Test

### Test Password Validation
```bash
# 1. Start app
python app.py

# 2. Login admin/admin123 (works - 8 chars)
# 3. Go to /admin/teachers
# 4. Try adding teacher with password "short" → Error flash
# 5. Try adding teacher with password "secure123" → Success
```

### Test Password Reset v2
```bash
# 1. Start app
python app.py

# 2. Go to login page → click "Forgot Password v2"
# 3. Enter admin email: admin@attendance-erp.local
# 4. Check console for reset URL (if no SMTP configured)
# 5. Open URL: http://localhost:5000/reset-password-v2?token=...
# 6. Enter new password (min 8 chars) → Success
# 7. Login with new password
```

### Configure Email (Optional)
Add to `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=your-email@gmail.com
```

---

## Architecture

```
User clicks "Forgot Password v2"
    → /forgot-password-v2 (POST email)
    → find_user_by_email()
    → generate_secure_token() [secrets module]
    → store_reset_token() [DB, 30-min expiry]
    → send_reset_email() [SMTP]

User clicks email link
    → /reset-password-v2?token=xxx (GET)
    → get_token_record() [verify valid + not used + not expired]
    → Show reset form

User submits new password
    → /reset-password-v2 (POST)
    → validate_password_length() [8+ chars]
    → update_user_password() [bcrypt hash]
    → mark_token_used() [single-use]
    → Redirect to login
