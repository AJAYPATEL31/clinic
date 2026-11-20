from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import DoctorCategory, Department, LoginLog, CustomUser
from .forms import AdminLoginForm, DoctorCategoryForm, DepartmentForm


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

@login_required(login_url='login')
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

    recent_categories = DoctorCategory.objects.select_related('department').order_by('-created_at')[:6]
    departments_summary = Department.objects.annotate(cat_count=Count('doctor_categories'))[:5]
    recent_logins = LoginLog.objects.filter(user=request.user).order_by('-login_time')[:5]

    context = {
        'total_categories': total_categories,
        'active_categories': active_categories,
        'total_departments': total_departments,
        'active_departments': active_departments,
        'recent_categories': recent_categories,
        'departments_summary': departments_summary,
        'recent_logins': recent_logins,
    }
    return render(request, 'hospital/dashboard.html', context)


# ==========================================
# Day 3: Doctor Category Management (CRUD + Listing Table)
# ==========================================

@login_required(login_url='login')
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


@login_required(login_url='login')
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


@login_required(login_url='login')
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


@login_required(login_url='login')
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

@login_required(login_url='login')
def department_list_view(request):
    """Department listing for managing hospital departments"""
    departments = Department.objects.annotate(doctor_count=Count('doctor_categories')).all()
    return render(request, 'hospital/department_list.html', {'departments': departments})


@login_required(login_url='login')
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


@login_required(login_url='login')
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


@login_required(login_url='login')
def department_delete_view(request, pk):
    """Delete department view"""
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept_name = dept.name
        dept.delete()
        messages.success(request, f"Department '{dept_name}' deleted successfully.")
        return redirect('department_list')
    return render(request, 'hospital/department_confirm_delete.html', {'department': dept})
