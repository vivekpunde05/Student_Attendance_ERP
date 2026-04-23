# Security Enhancement TODO - Progress Tracker

## Plan Overview
✅ **Phase 1**: Password validation (8+ chars)  
🔄 **Phase 2**: Forgot password feature  

**Current Progress: 7/18 steps complete** (Phase 1 ✅)

### Phase 1: Password Validation ✅
1. ✅ Read `utils.py` & `config.py`  
2. ✅ Add `validate_password_length()` to `utils.py`  
3. ✅ Update `admin.py`: `add_teacher()` validation  
4. ✅ Update `admin.py`: `admin_login()` validation  
5. ✅ Update `teacher.py`: `teacher_login()` validation  
6. ✅ Update `app.py`: `admin_add_teacher()` error handling  
7. ✅ Client-side JS validation + HTML5 minlength on admin/teachers.html

### Phase 2: Forgot Password
8. ✅ Update `config.py` (EMAIL_* vars added)  
9. ✅ Update `database.py`: reset_token/expires for admins/teachers  
10. ✅ Email utils in `utils.py`: `generate_reset_token()`, `send_reset_email()`
11. ✅ `/forgot-password` route + logic (app.py)  
12. ✅ `/reset-password/<token>` route + logic (app.py)  
13. ✅ `forgot_password.html` created  
14. ✅ `reset_password.html` created  
15. ✅ `login.html`: Forgot pw link added  
16. ✅ `admin/teachers.html`: Password hint added  
17. [ ] DB migration: Run ALTER TABLE manually  
18. [ ] Test complete flow + README.md update  

## Test Password Validation Now
```
1. Login admin/admin123 (works)
2. Go /admin/teachers → Add teacher with pw <8 chars → Error flash
3. Login attempt with short pw → Fails silently
```

**Next: Step 7 (JS validation) then Phase 2**
