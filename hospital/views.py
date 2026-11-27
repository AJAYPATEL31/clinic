from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import DoctorCategory, Department, LoginLog, CustomUser, DoctorRegister, UserRegistration, UserRegister
from .forms import AdminLoginForm, DoctorCategoryForm, DepartmentForm, DoctorRegisterForm, UserRegisterForm


def admin_required(view_func):
    """
    Task 2: Restrict view access to authenticated admin users only.
    - If user is not authenticated: redirects to login page.
    - If user is authenticated but not an Admin (and not staff/superuser): returns 403 Forbidden
      and displays an access restriction notice.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        if not (request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'Admin'):
            messages.error(request, "Access restricted: Administrator privileges are required to view this page.")
            return render(request, 'hospital/access_denied.html', {
                'title': 'Access Restricted',
                'user': request.user
            }, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def get_client_ip(request):
    """Helper to extract visitor IP address for LoginLog"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ==========================================
# Day 1 & Day 2: Admin Login & Logout Views
# ==========================================

def admin_login_view(request):
    """
    Day 1 Task 3 & Day 2 Task 1:
    Admin login page using Email & Password via Django's auth system (No signup).
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email').strip().lower()
            password = form.cleaned_data.get('password')

            # Django's authenticate uses USERNAME_FIELD which is email
            user = authenticate(request, username=email, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account has been deactivated. Please contact the administrator.")
                elif not (user.is_superuser or user.is_staff or user.role == 'Admin'):
                    messages.error(request, "Access restricted. Only authorized superusers/administrators can log in.")
                else:
                    login(request, user)
                    
                    # Record login in LoginLog model (Day 2 model requirement)
                    LoginLog.objects.create(
                        user=user,
                        login_time=timezone.now(),
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:250],
                        status='Success'
                    )

                    messages.success(request, f"Welcome, {user.first_name or user.email}! Logged in as Superuser / Admin.")
                    next_url = request.GET.get('next')
                    return redirect(next_url if next_url else 'dashboard')
            else:
                messages.error(request, "Invalid email address or password. Please verify your superuser credentials.")
    else:
        form = AdminLoginForm()

    return render(request, 'hospital/login.html', {'form': form})


@login_required(login_url='login')
def admin_logout_view(request):
    """
    Day 2 Task 1: Logout view using Django's auth system.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully. Have a great day!")
    return redirect('login')


# ==========================================
# Day 2: Admin Dashboard (Visible only to logged-in admin users)
# ==========================================

@admin_required
def admin_dashboard_view(request):
    """
    Day 2 Task 2:
    Dashboard page visible only to logged-in admin users.
    Displays metrics, quick actions, recent categories, and login log history.
    """
    total_categories = DoctorCategory.objects.count()
    active_categories = DoctorCategory.objects.filter(is_active=True).count()
    total_departments = Department.objects.count()
    active_departments = Department.objects.filter(is_active=True).count()
    total_doctors = DoctorRegister.objects.count()
    active_doctors = DoctorRegister.objects.filter(is_active=True).count()

    recent_categories = DoctorCategory.objects.select_related('department').order_by('-created_at')[:6]
    departments_summary = Department.objects.annotate(cat_count=Count('doctor_categories'))[:5]
    recent_logins = LoginLog.objects.filter(user=request.user).order_by('-login_time')[:5]
    recent_doctors = DoctorRegister.objects.select_related('department', 'category').order_by('-registration_date')[:5]

    context = {
        'total_categories': total_categories,
        'active_categories': active_categories,
        'total_departments': total_departments,
        'active_departments': active_departments,
        'total_doctors': total_doctors,
        'active_doctors': active_doctors,
        'recent_categories': recent_categories,
        'departments_summary': departments_summary,
        'recent_logins': recent_logins,
        'recent_doctors': recent_doctors,
    }
    return render(request, 'hospital/dashboard.html', context)


# ==========================================
# Day 3: Doctor Category Management (CRUD + Listing Table)
# ==========================================

@admin_required
def category_list_view(request):
    """
    Day 3 Task 1 & Task 3:
    Admin interface for listing doctor categories with search and filter.
    """
    search_query = request.GET.get('q', '').strip()
    selected_dept = request.GET.get('department', '').strip()
    status_filter = request.GET.get('status', '').strip()

    categories = DoctorCategory.objects.select_related('department').all()

    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

    if selected_dept:
        categories = categories.filter(department_id=selected_dept)

    if status_filter == 'active':
        categories = categories.filter(is_active=True)
    elif status_filter == 'inactive':
        categories = categories.filter(is_active=False)

    departments = Department.objects.filter(is_active=True)

    context = {
        'categories': categories,
        'departments': departments,
        'search_query': search_query,
        'selected_dept': selected_dept,
        'status_filter': status_filter,
        'total_found': categories.count(),
    }
    return render(request, 'hospital/category_list.html', context)


@admin_required
def category_add_view(request):
    """
    Day 3 Task 2: Add doctor category view
    """
    if request.method == 'POST':
        form = DoctorCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Doctor Category '{category.name}' created successfully!")
            return redirect('category_list')
        else:
            messages.error(request, "Please check the form fields and correct the errors below.")
    else:
        form = DoctorCategoryForm()

    departments_exist = Department.objects.exists()
    return render(request, 'hospital/category_form.html', {
        'form': form,
        'title': 'Add New Doctor Category',
        'is_edit': False,
        'departments_exist': departments_exist,
    })


@admin_required
def category_edit_view(request, pk):
    """
    Day 3 Task 2: Edit doctor category view
    """
    category = get_object_or_404(DoctorCategory, pk=pk)

    if request.method == 'POST':
        form = DoctorCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Doctor Category '{category.name}' updated successfully!")
            return redirect('category_list')
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        form = DoctorCategoryForm(instance=category)

    return render(request, 'hospital/category_form.html', {
        'form': form,
        'category': category,
        'title': f"Edit Category: {category.name}",
        'is_edit': True,
        'departments_exist': True,
    })


@admin_required
def category_delete_view(request, pk):
    """
    Day 3 Task 2: Delete doctor category view
    """
    category = get_object_or_404(DoctorCategory, pk=pk)

    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f"Doctor Category '{category_name}' has been deleted successfully.")
        return redirect('category_list')

    return render(request, 'hospital/category_confirm_delete.html', {'category': category})


# ==========================================
# Bonus / Day 2 Department Management Views
# ==========================================

@admin_required
def department_list_view(request):
    """Department listing for managing hospital departments"""
    departments = Department.objects.annotate(doctor_count=Count('doctor_categories')).all()
    return render(request, 'hospital/department_list.html', {'departments': departments})


@admin_required
def department_add_view(request):
    """Add new department view"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' added successfully!")
            return redirect('department_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm()
    return render(request, 'hospital/department_form.html', {'form': form, 'title': 'Add Department', 'is_edit': False})


@admin_required
def department_edit_view(request, pk):
    """Edit department view"""
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            dept = form.save()
            messages.success(request, f"Department '{dept.name}' updated successfully!")
            return redirect('department_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'hospital/department_form.html', {'form': form, 'department': dept, 'title': f"Edit Department: {dept.name}", 'is_edit': True})


@admin_required
def department_delete_view(request, pk):
    """Delete department view"""
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept_name = dept.name
        dept.delete()
        messages.success(request, f"Department '{dept_name}' deleted successfully.")
        return redirect('department_list')
    return render(request, 'hospital/department_confirm_delete.html', {'department': dept})


# ==========================================
# Task: Manual Doctor Registration & Listing Views
# ==========================================

@admin_required
def doctor_register_view(request):
    """
    Task 1 & 2: Form handling in Django views, input validation, upload & save doctor photo.
    """
    if request.method == 'POST':
        # Handles both text data (POST) and file uploads (FILES)
        form = DoctorRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Doctor Dr. {doctor.full_name} has been successfully registered!")
            # Task 3: Display confirmation
            return redirect('doctor_confirmation', pk=doctor.pk)
        else:
            messages.error(request, "Form validation failed. Please correct the highlighted errors below.")
    else:
        form = DoctorRegisterForm()

    departments = Department.objects.filter(is_active=True)
    categories = DoctorCategory.objects.filter(is_active=True).select_related('department')

    return render(request, 'hospital/doctor_register.html', {
        'form': form,
        'departments': departments,
        'categories': categories,
        'title': 'Manual Doctor Registration',
    })


@admin_required
def doctor_confirmation_view(request, pk):
    """
    Task 3: Display confirmation of registered doctor
    """
    doctor = get_object_or_404(DoctorRegister.objects.select_related('department', 'category'), pk=pk)
    return render(request, 'hospital/doctor_confirmation.html', {'doctor': doctor})


@admin_required
def doctor_edit_view(request, pk):
    """
    Task 2: Implement edit doctor functionality with prefilled form
    """
    doctor = get_object_or_404(DoctorRegister, pk=pk)
    if request.method == 'POST':
        # Form handling: pass POST data, uploaded files, and the existing doctor instance
        form = DoctorRegisterForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Doctor Dr. {doctor.full_name}'s information has been updated successfully!")
            return redirect('doctor_list')
        else:
            messages.error(request, "Please correct the highlighted errors below before saving.")
    else:
        # GET request: prefill form with existing doctor data
        form = DoctorRegisterForm(instance=doctor)

    departments = Department.objects.filter(is_active=True)
    categories = DoctorCategory.objects.filter(is_active=True).select_related('department')

    return render(request, 'hospital/doctor_edit.html', {
        'form': form,
        'doctor': doctor,
        'departments': departments,
        'categories': categories,
        'title': f"Edit Doctor: Dr. {doctor.full_name}",
        'is_edit': True,
    })




@admin_required
def doctor_list_view(request):
    """
    Task 1: View list of all registered doctors with search, filter, and pagination.
    """
    search_query = request.GET.get('q', '').strip()
    selected_dept = request.GET.get('department', '').strip()
    selected_cat = request.GET.get('category', '').strip()

    doctors_qs = DoctorRegister.objects.select_related('department', 'category').all().order_by('-id')

    if search_query:
        doctors_qs = doctors_qs.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(qualification__icontains=search_query) |
            Q(room_number__icontains=search_query)
        )

    if selected_dept:
        doctors_qs = doctors_qs.filter(department_id=selected_dept)

    if selected_cat:
        doctors_qs = doctors_qs.filter(category_id=selected_cat)

    total_doctors = doctors_qs.count()

    # Pagination: default 6 doctors per page
    per_page = request.GET.get('per_page', 6)
    try:
        per_page = int(per_page)
        if per_page < 1:
            per_page = 6
    except (ValueError, TypeError):
        per_page = 6

    paginator = Paginator(doctors_qs, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    departments = Department.objects.filter(is_active=True)
    categories = DoctorCategory.objects.filter(is_active=True)

    return render(request, 'hospital/doctor_list.html', {
        'doctors': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'departments': departments,
        'categories': categories,
        'search_query': search_query,
        'selected_dept': selected_dept,
        'selected_cat': selected_cat,
        'total_doctors': total_doctors,
        'is_paginated': page_obj.has_other_pages(),
    })


@admin_required
def doctor_delete_view(request, pk):
    """Delete a registered doctor"""
    doctor = get_object_or_404(DoctorRegister, pk=pk)
    if request.method == 'POST':
        name = doctor.full_name
        doctor.delete()
        messages.success(request, f"Doctor Dr. {name} has been removed.")
        return redirect('doctor_list')
    return render(request, 'hospital/doctor_confirm_delete.html', {'doctor': doctor})


# ==========================================
# Task 3: User / Staff Registration View
# ==========================================

def user_register_view(request):
    """
    Backend form handler for user registration:
    - Validates form inputs, email uniqueness, and strong password rules.
    - Creates CustomUser account and saves registration data to UserRegister model.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            contact_number = form.cleaned_data['contact_number']
            role = form.cleaned_data['role']
            password = form.cleaned_data['password']

            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            is_admin = (role == 'Admin')

            try:
                with transaction.atomic():
                    user = CustomUser.objects.create_user(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        phone=contact_number,
                        role=role,
                        is_staff=is_admin,
                        is_superuser=is_admin,
                        is_active=True
                    )

                    registration = form.save(commit=False)
                    registration.user = user
                    registration.email = email
                    registration.save()
            except IntegrityError:
                form.add_error('email', "An account with this email address already exists.")
                messages.error(request, "Registration failed. This email address is already registered.")
            else:
                messages.success(request, f"Registration successful for {full_name}! You can now sign in with your credentials.")
                return redirect('login')
        else:
            messages.error(request, "Registration failed. Please check the highlighted fields below.")
    else:
        form = UserRegisterForm()

    return render(request, 'hospital/register.html', {
        'form': form,
        'title': 'User Registration - Clinic On',
    })


