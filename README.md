# Clinic On - Hospital Management System

A full-featured Django web application developed for **Clinic On - Hospital Management System**, covering all Day 1, Day 2, and Day 3 requirements.

---

## 📌 Three-Day Roadmap & Implementation Summary

### 🗓️ Day 1: Project Setup & Authentication UI
1. **Django Project & App Creation**:
   - Project: `clinicon`
   - App: `hospital`
2. **Settings Configuration**:
   - **Database**: SQLite3 configured (`db.sqlite3`).
   - **Static Files**: `STATIC_URL`, `STATICFILES_DIRS = [BASE_DIR / 'static']`, `STATIC_ROOT`.
   - **Templates**: `BASE_DIR / 'templates'` registered with Django template engine.
   - **Media Files**: `MEDIA_URL` & `MEDIA_ROOT`.
   - **Timezone**: Set to `Asia/Kolkata`.
3. **HTML Admin Login Page (No Signup)**:
   - Designed at `templates/hospital/login.html` with clean hospital branding.
   - Fields: **Email Address** and **Password** (password visibility toggle).
   - Strictly **no registration / signup links**, adhering to admin specifications.
   - Includes quick credentials autofill button for test convenience.

---

### 🗓️ Day 2: Authentication System, Dashboard & Core Models
1. **Django Auth System (Login & Logout)**:
   - **`CustomUser` Model** (`AbstractUser`): Uses `email` as `USERNAME_FIELD` (unique identifier) instead of username.
   - **`UserRegistration` Model**: Tracks registered admin/staff profiles.
   - **`LoginLog` Model**: Automatically records login timestamps, user agents, and IP addresses.
   - Login view (`admin_login_view`) and logout view (`admin_logout_view`) with user session handling.
2. **Protected Admin Dashboard**:
   - Access restricted with `@login_required(login_url='login')`.
   - Displays real-time statistics:
     - Total & active Doctor Categories
     - Total & active Hospital Departments
     - System & authentication security status
     - Recent categories quick view
     - Recent login history log
3. **Models for DoctorCategory & Department**:
   - **`Department` Model**:
     - `name`, `code`, `description`, `head_of_department`, `is_active`, timestamps.
   - **`DoctorCategory` Model**:
     - `name`, `department` (ForeignKey), `description`, `consultation_fee`, `is_active`, timestamps.

---

### 🗓️ Day 3: Doctor Category Management (Admin Interface & Full CRUD)
1. **Admin Interface (HTML page)**:
   - Dedicated Category Management page (`templates/hospital/category_list.html`).
   - Filter by Department, Filter by Active/Inactive status, and live search bar.
2. **Add / Edit / Delete Views**:
   - **Add**: `category_add_view` (`templates/hospital/category_form.html`).
   - **Edit**: `category_edit_view` (Pre-populated form with existing data).
   - **Delete**: `category_delete_view` (`templates/hospital/category_confirm_delete.html` with safety confirmation).
3. **Category Listing Table**:
   - Responsive Bootstrap 5 table with:
     - S.No, Category Name, Department badge, Consultation Fee (₹), Description, Status badge, Creation Date, Action buttons (Edit & Delete).
   - Clean empty state when no categories exist with quick create CTA.

---

## 🚀 Quick Start Guide

### 1. Run Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py seed_data
```

### 2. Start the Development Server
```bash
python manage.py runserver
```

Open your browser at: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Default Admin Credentials

| Role | Email | Password |
|---|---|---|
| **System Administrator** | `admin@clinicon.com` | `admin123` |

*(You can also access the Django default admin panel at `http://127.0.0.1:8000/django-admin/`)*

---

## 🧪 Run Automated Tests
All 10 test cases verify models, authentication, security redirects, and Day 3 CRUD operations:
```bash
python manage.py test
```
Result:
```text
Ran 10 tests in ...
OK
```

---

## 📂 Project Structure
```text
clinicOn/
│
├── clinicon/                  # Project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py            # Day 1: DB, Static, Templates, Auth configured
│   ├── urls.py                # Main project routing
│   └── wsgi.py
│
├── hospital/                  # Core application
│   ├── management/commands/
│   │   └── seed_data.py       # Auto-seeds default admin, departments & categories
│   ├── migrations/            # Database schema migrations
│   ├── admin.py               # Django Admin registration
│   ├── apps.py
│   ├── forms.py               # LoginForm, DoctorCategoryForm, DepartmentForm
│   ├── models.py              # CustomUser, UserRegistration, LoginLog, Department, DoctorCategory
│   ├── tests.py               # Full test suite covering Day 1, 2, and 3
│   ├── urls.py                # App URL patterns
│   └── views.py               # Login, Logout, Dashboard, Category CRUD views
│
├── templates/
│   ├── base.html              # Modern hospital dashboard base template
│   └── hospital/
│       ├── login.html         # Day 1: Admin login (Email + Password, No signup)
│       ├── dashboard.html     # Day 2: Protected Admin dashboard
│       ├── category_list.html # Day 3: Category listing table with search/filter
│       ├── category_form.html # Day 3: Add & Edit doctor category
│       ├── category_confirm_delete.html # Day 3: Delete category confirmation
│       ├── department_list.html
│       ├── department_form.html
│       └── department_confirm_delete.html
│
├── static/
│   ├── css/custom.css         # Custom hospital styling
│   └── js/main.js             # Alert auto-dismiss and UI helpers
│
├── db.sqlite3                 # SQLite database
├── manage.py
└── README.md
```
