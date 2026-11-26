from django import forms
from .models import DoctorCategory, Department, DoctorRegister, CustomUser, UserRegistration


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
    Form for manual Doctor Registration in HTML with photo upload and validation
    """
    class Meta:
        model = DoctorRegister
        fields = [
            'full_name', 'email', 'phone', 'photo', 'department', 'category',
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
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'docPhoto',
                'accept': 'image/*'
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

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if len(name) < 3:
            raise forms.ValidationError("Doctor full name must be at least 3 characters long.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        # Remove common phone separators
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 8:
            raise forms.ValidationError("Please provide a valid contact number (at least 8 digits).")
        return phone

    def clean_consultation_fee(self):
        fee = self.cleaned_data.get('consultation_fee')
        if fee is not None and fee < 0:
            raise forms.ValidationError("Consultation fee cannot be negative.")
        return fee

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # 5MB limit
            max_size = 5 * 1024 * 1024
            if photo.size > max_size:
                raise forms.ValidationError("Doctor photo size must be less than 5MB.")
            # Check content type / extension
            valid_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
            if hasattr(photo, 'content_type') and photo.content_type not in valid_types:
                raise forms.ValidationError("Please upload a valid image file (JPEG, PNG, or WebP).")
        return photo


class UserRegisterForm(forms.ModelForm):
    """
    Task 3: User / Admin Registration Form with proper fields and validation
    """
    full_name = forms.CharField(
        max_length=150,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Dr. Rajesh Sharma, Priya Patel',
            'id': 'regFullName',
            'required': True
        })
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@clinicon.com',
            'id': 'regEmail',
            'required': True
        })
    )
    contact_number = forms.CharField(
        max_length=20,
        label="Contact Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91 98765 43210',
            'id': 'regContact',
            'required': True
        })
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        label="Account Role",
        initial='Admin',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'regRole',
            'required': True
        })
    )
    department_name = forms.CharField(
        max_length=100,
        label="Department / Unit",
        initial='Administration',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Administration, Cardiology, Emergency',
            'id': 'regDepartment',
            'required': True
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'id': 'regPassword',
            'required': True
        })
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            'id': 'regConfirmPassword',
            'required': True
        })
    )

    class Meta:
        model = UserRegistration
        fields = ['full_name', 'email', 'contact_number', 'department_name']

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if len(name) < 3:
            raise forms.ValidationError("Full name must be at least 3 characters long.")
        return name

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number', '').strip()
        digits = ''.join(filter(str.isdigit, contact))
        if len(digits) < 8:
            raise forms.ValidationError("Please provide a valid contact number (at least 8 digits).")
        return contact

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and len(password) < 6:
            self.add_error('password', "Password must be at least 6 characters long.")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


