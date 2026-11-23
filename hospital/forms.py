from django import forms
from .models import DoctorCategory, Department, DoctorRegister


class AdminLoginForm(forms.Form):
    """
    Day 1 & Day 2: Form for Admin Login using Email and Password
    """
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@clinicon.com',
            'id': 'emailInput',
            'autocomplete': 'email',
            'required': True
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'id': 'passwordInput',
            'autocomplete': 'current-password',
            'required': True
        })
    )


class DoctorCategoryForm(forms.ModelForm):
    """
    Day 3: Model Form for Doctor Category Add/Edit
    """
    class Meta:
        model = DoctorCategory
        fields = ['name', 'department', 'consultation_fee', 'is_active', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Senior Cardiologist, Pediatric Surgeon',
                'required': True
            }),
            'department': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'consultation_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '10.00',
                'min': '0',
                'placeholder': '500.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide details on required qualifications, responsibilities, or special notes...'
            }),
        }


class DepartmentForm(forms.ModelForm):
    """
    Model Form for Department management
    """
    class Meta:
        model = Department
        fields = ['name', 'code', 'head_of_department', 'is_active', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Cardiology, Neurology',
                'required': True
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. CARD-01, NEUR-02'
            }),
            'head_of_department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Dr. Rajesh Sharma'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Department description and scope...'
            }),
        }


class DoctorRegisterForm(forms.ModelForm):
    """
    Form for manual Doctor Registration in HTML
    """
    class Meta:
        model = DoctorRegister
        fields = [
            'full_name', 'email', 'phone', 'department', 'category',
            'qualification', 'experience_years', 'consultation_fee',
            'room_number', 'address', 'is_active'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'docFullName',
                'placeholder': 'e.g. Dr. Ramesh Kumar',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'docEmail',
                'placeholder': 'doctor@clinicon.com',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'docPhone',
                'placeholder': '+91 98765 43210',
                'required': True
            }),
            'department': forms.Select(attrs={
                'class': 'form-select',
                'id': 'docDepartment',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'docCategory',
                'required': True
            }),
            'qualification': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'docQualification',
                'placeholder': 'e.g. MBBS, MD (Cardiology)',
                'required': True
            }),
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'docExperience',
                'min': '0',
                'placeholder': '5',
                'required': True
            }),
            'consultation_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'docFee',
                'step': '10.00',
                'min': '0',
                'placeholder': '500.00',
                'required': True
            }),
            'room_number': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'docRoom',
                'placeholder': 'OPD Room 104'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'docAddress',
                'rows': 2,
                'placeholder': 'Clinic / Residential address'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            }),
        }

