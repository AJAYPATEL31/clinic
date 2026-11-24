from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils import timezone


# ==========================================
# Day 2: Custom User & Registration/Login Models
# ==========================================

class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be provided')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        username = extra_fields.get('username') or email.split('@')[0]
        extra_fields['username'] = username
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'Admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom User model for Clinic On with email as primary login field.
    """
    ROLE_CHOICES = (
        ('Admin', 'Administrator'),
        ('Doctor', 'Doctor'),
        ('Staff', 'Hospital Staff'),
    )

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name='Email Address')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone Number')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Admin')
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"


class UserRegistration(models.Model):
    """
    Registration record model for Hospital Admin / Staff.
    Stores registration profile linked with auth system.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registration_record'
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    department_name = models.CharField(max_length=100, default='Administration')
    registered_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'User Registration'
        verbose_name_plural = 'User Registrations'
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class LoginLog(models.Model):
    """
    Login history model tracking admin login events.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_logs'
    )
    login_time = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Success')

    class Meta:
        verbose_name = 'Login Log'
        verbose_name_plural = 'Login Logs'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.email} - {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}"


# ==========================================
# Day 2 & Day 3: Department & Doctor Category Models
# ==========================================

class Department(models.Model):
    """
    Hospital Department model (e.g., Cardiology, Neurology, Pediatrics).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='Department Name')
    code = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='Department Code')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    head_of_department = models.CharField(max_length=100, blank=True, null=True, verbose_name='Head of Department (HOD)')
    is_active = models.BooleanField(default=True, verbose_name='Active Status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']

    def __str__(self):
        return self.name


class DoctorCategory(models.Model):
    """
    Doctor Category / Specialization model (e.g., Senior Cardiologist, Resident Surgeon).
    Day 3 CRUD operations manage this model.
    """
    name = models.CharField(max_length=120, verbose_name='Category Name')
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='doctor_categories',
        verbose_name='Department'
    )
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500.00,
        verbose_name='Standard Consultation Fee (₹)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Doctor Category'
        verbose_name_plural = 'Doctor Categories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.department.name})"


# ==========================================
# Task: Doctor Registration Model
# ==========================================

class DoctorRegister(models.Model):
    """
    Model for manual Doctor Registration in Clinic On system.
    Stores doctor's professional details, department, and category.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_profile'
    )
    full_name = models.CharField(max_length=150, verbose_name='Doctor Full Name')
    email = models.EmailField(unique=True, verbose_name='Email Address')
    phone = models.CharField(max_length=20, verbose_name='Contact Phone')
    photo = models.ImageField(
        upload_to='doctor_photos/',
        blank=True,
        null=True,
        verbose_name='Doctor Photo'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='registered_doctors',
        verbose_name='Department'
    )
    category = models.ForeignKey(
        DoctorCategory,
        on_delete=models.CASCADE,
        related_name='registered_doctors',
        verbose_name='Doctor Category / Specialization'
    )
    qualification = models.CharField(max_length=120, verbose_name='Qualification', help_text='e.g. MBBS, MD, MS, DM')
    experience_years = models.PositiveIntegerField(default=1, verbose_name='Experience (Years)')
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=500.00,
        verbose_name='Consultation Fee (₹)'
    )
    room_number = models.CharField(max_length=30, blank=True, null=True, verbose_name='OPD Room / Cabin')
    address = models.TextField(blank=True, null=True, verbose_name='Residential / Clinic Address')
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name='Registration Date')
    is_active = models.BooleanField(default=True, verbose_name='Active Status')

    class Meta:
        verbose_name = 'Doctor Registration'
        verbose_name_plural = 'Doctor Registrations'
        ordering = ['-registration_date']

    def __str__(self):
        return f"Dr. {self.full_name} ({self.category.name})"


# Alias for compatibility
DoctorRegistration = DoctorRegister

