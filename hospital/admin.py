from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRegistration, LoginLog, Department, DoctorCategory, DoctorRegister


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'phone', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'phone')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name', 'phone', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'phone', 'is_staff', 'is_active'),
        }),
    )


@admin.register(UserRegistration)
class UserRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'contact_number', 'department_name', 'registered_at', 'is_active')
    search_fields = ('full_name', 'email', 'contact_number')
    list_filter = ('is_active', 'department_name')


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address', 'status')
    list_filter = ('status', 'login_time')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('user', 'login_time', 'ip_address', 'user_agent', 'status')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'head_of_department', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'head_of_department')
    list_filter = ('is_active',)


@admin.register(DoctorCategory)
class DoctorCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'consultation_fee', 'is_active', 'created_at')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'department__name', 'description')


@admin.register(DoctorRegister)
class DoctorRegisterAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'department', 'category', 'qualification', 'is_active')
    list_filter = ('department', 'category', 'is_active')
    search_fields = ('full_name', 'email', 'phone', 'qualification')

