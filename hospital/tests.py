from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from hospital.models import CustomUser, UserRegistration, LoginLog, Department, DoctorCategory, DoctorRegister


class ClinicOnProjectTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test admin user (Day 1 & Day 2)
        self.admin_email = 'testadmin@clinicon.com'
        self.admin_password = 'adminpassword123'
        self.admin_user = CustomUser.objects.create_superuser(
            email=self.admin_email,
            password=self.admin_password,
            first_name='Admin',
            last_name='User',
            role='Admin'
        )

        # Create department (Day 2)
        self.department = Department.objects.create(
            name='Cardiology',
            code='CARD-01',
            head_of_department='Dr. Rajesh Sharma',
            description='Heart and cardiovascular treatment'
        )

        # Create doctor category (Day 2 & Day 3)
        self.category = DoctorCategory.objects.create(
            name='Senior Cardiologist',
            department=self.department,
            consultation_fee=1000.00,
            description='Specialist in coronary procedures',
            is_active=True
        )

    # ----------------------------------------------------
    # Day 1 Tests: Settings, Project, HTML Login Page
    # ----------------------------------------------------
    def test_login_page_renders_html_without_signup(self):
        """Day 1 Task 3: HTML login page with email & password (no signup)"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hospital/login.html')
        content = response.content.decode('utf-8')
        self.assertIn('email', content.lower())
        self.assertIn('password', content.lower())
        self.assertNotIn('sign up', content.lower())
        self.assertNotIn('register here', content.lower())

    # ----------------------------------------------------
    # Day 2 Tests: Auth System, Login/Logout, Dashboard, Models
    # ----------------------------------------------------
    def test_models_exist_and_persist(self):
        """Day 2 Task 1 & 3: Login/Register models and DoctorCategory/Department models"""
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(Department.objects.count(), 1)
        self.assertEqual(DoctorCategory.objects.count(), 1)

        # UserRegistration model
        reg = UserRegistration.objects.create(
            user=self.admin_user,
            full_name='Admin User',
            email=self.admin_email,
            contact_number='1234567890'
        )
        self.assertEqual(UserRegistration.objects.count(), 1)
        self.assertEqual(str(reg), f"Admin User ({self.admin_email})")

    def test_login_success_and_loginlog_created(self):
        """Day 2 Task 1: Login using Django auth with email and password"""
        response = self.client.post(reverse('login'), {
            'email': self.admin_email,
            'password': self.admin_password,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Should redirect to dashboard
        self.assertTrue(response.context['user'].is_authenticated)
        # Should have recorded in LoginLog
        self.assertEqual(LoginLog.objects.filter(user=self.admin_user).count(), 1)

    def test_login_failure_with_wrong_password(self):
        """Day 2 Task 1: Login with invalid password fails"""
        response = self.client.post(reverse('login'), {
            'email': self.admin_email,
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_dashboard_visible_only_to_logged_in_users(self):
        """Day 2 Task 2: Dashboard is protected, anonymous users redirected to login"""
        # Anonymous request
        anon_response = self.client.get(reverse('dashboard'))
        self.assertEqual(anon_response.status_code, 302)
        self.assertIn('/login/', anon_response.url)

        # Logged in request
        self.client.login(username=self.admin_email, password=self.admin_password)
        auth_response = self.client.get(reverse('dashboard'))
        self.assertEqual(auth_response.status_code, 200)
        self.assertTemplateUsed(auth_response, 'hospital/dashboard.html')

    def test_logout_redirects_to_login(self):
        """Day 2 Task 1: Logout works and redirects to login"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        logout_response = self.client.get(reverse('logout'), follow=True)
        self.assertFalse(logout_response.context['user'].is_authenticated)
        self.assertTemplateUsed(logout_response, 'hospital/login.html')

    # ----------------------------------------------------
    # Day 3 Tests: Doctor Category Management (CRUD + Listing Table)
    # ----------------------------------------------------
    def test_category_list_table_page(self):
        """Day 3 Task 1 & 3: Category listing table page"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hospital/category_list.html')
        self.assertIn('Senior Cardiologist', response.content.decode('utf-8'))
        self.assertIn('₹1000.00', response.content.decode('utf-8'))

    def test_category_add_view(self):
        """Day 3 Task 2: Add doctor category view"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        response = self.client.post(reverse('category_add'), {
            'name': 'Pediatric Cardiologist',
            'department': self.department.id,
            'consultation_fee': '1100.00',
            'description': 'Children heart defect specialist',
            'is_active': True,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(DoctorCategory.objects.filter(name='Pediatric Cardiologist').exists())

    def test_category_edit_view(self):
        """Day 3 Task 2: Edit doctor category view"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        response = self.client.post(reverse('category_edit', args=[self.category.pk]), {
            'name': 'Chief Cardiologist',
            'department': self.department.id,
            'consultation_fee': '1500.00',
            'description': 'Head of heart surgery unit',
            'is_active': True,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Chief Cardiologist')
        self.assertEqual(float(self.category.consultation_fee), 1500.00)

    def test_category_delete_view(self):
        """Day 3 Task 2: Delete doctor category view"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        response = self.client.post(reverse('category_delete', args=[self.category.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(DoctorCategory.objects.filter(pk=self.category.pk).exists())

    # ----------------------------------------------------
    # New Task Tests: Frontend Validation & Doctor Registration
    # ----------------------------------------------------
    def test_category_frontend_validation_markup(self):
        """Task 1: Category form includes frontend validation attributes & script"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        response = self.client.get(reverse('category_add'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Check form id and novalidate
        self.assertIn('id="categoryForm"', content)
        self.assertIn('novalidate', content)
        # Check invalid-feedback containers
        self.assertIn('invalid-feedback', content)
        self.assertIn('nameFeedback', content)
        self.assertIn('feeFeedback', content)
        # Check frontend validation JS
        self.assertIn('validateName', content)
        self.assertIn('validateDepartment', content)
        self.assertIn('validateFee', content)

    def test_doctor_register_model_and_creation(self):
        """Task 2: Use DoctorRegister model to store doctor details"""
        doc = DoctorRegister.objects.create(
            full_name='Dr. Test Kumar',
            email='test.kumar@clinicon.com',
            phone='+91 99999 88888',
            department=self.department,
            category=self.category,
            qualification='MBBS, MD',
            experience_years=8,
            consultation_fee=900.00,
            room_number='OPD 101'
        )
        self.assertEqual(DoctorRegister.objects.count(), 1)
        self.assertIn('Dr. Dr. Test Kumar', str(doc))

    def test_manual_doctor_registration_view(self):
        """Task 3: Manual doctor registration form in HTML (GET & POST)"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        # GET form page
        get_resp = self.client.get(reverse('doctor_register'))
        self.assertEqual(get_resp.status_code, 200)
        self.assertTemplateUsed(get_resp, 'hospital/doctor_register.html')
        content = get_resp.content.decode('utf-8')
        self.assertIn('Manual Doctor Registration', content)
        self.assertIn('id="doctorRegisterForm"', content)
        self.assertIn('enctype="multipart/form-data"', content)

        # POST form submission with photo upload
        small_image = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n'
            b'\x08\x02\x00\x00\x00\x02PX\xea\x00\x00\x00\x13IDATx\x9cc\xfc\xcf'
            b'\x80\x0f0\xe1\x95e\x18\xa9\xd2\x00A,\x01\x13y\xed\xba&\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        photo = SimpleUploadedFile('doctor_test.png', small_image, content_type='image/png')

        post_resp = self.client.post(reverse('doctor_register'), {
            'full_name': 'Anil Deshmukh',
            'email': 'dr.anil@clinicon.com',
            'phone': '+91 91234 56789',
            'department': self.department.id,
            'category': self.category.id,
            'qualification': 'MBBS, MS (General Surgery)',
            'experience_years': 10,
            'consultation_fee': '750.00',
            'room_number': 'Cabin 202',
            'address': 'Staff Quarters, Clinic On',
            'photo': photo,
            'is_active': True,
        }, follow=True)

        self.assertEqual(post_resp.status_code, 200)
        doctor = DoctorRegister.objects.filter(email='dr.anil@clinicon.com').first()
        self.assertIsNotNone(doctor)
        self.assertTrue(bool(doctor.photo))
        # Checks confirmation page is displayed
        self.assertTemplateUsed(post_resp, 'hospital/doctor_confirmation.html')
        self.assertIn('Doctor Registration Confirmed', post_resp.content.decode('utf-8'))

    def test_doctor_form_input_validation(self):
        """Task 2: Validate form inputs on server side"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        # Invalid: short name, negative fee, short phone
        invalid_resp = self.client.post(reverse('doctor_register'), {
            'full_name': 'A',
            'email': 'invalid-email',
            'phone': '123',
            'department': self.department.id,
            'category': self.category.id,
            'qualification': '',
            'experience_years': 0,
            'consultation_fee': '-50.00',
        })
        self.assertEqual(invalid_resp.status_code, 200)
        form = invalid_resp.context['form']
        self.assertFormError(form, 'full_name', 'Doctor full name must be at least 3 characters long.')
        self.assertFormError(form, 'phone', 'Please provide a valid contact number (at least 8 digits).')
        self.assertFormError(form, 'consultation_fee', 'Consultation fee cannot be negative.')

    def test_doctor_list_and_delete_view(self):
        """Test Doctor listing table and delete functionality"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        doc = DoctorRegister.objects.create(
            full_name='Vikram Seth',
            email='dr.vikram@clinicon.com',
            phone='+91 95555 44444',
            department=self.department,
            category=self.category,
            qualification='MBBS',
            experience_years=4,
            consultation_fee=500.00
        )
        # Listing table
        list_resp = self.client.get(reverse('doctor_list'))
        self.assertEqual(list_resp.status_code, 200)
        self.assertIn('Vikram Seth', list_resp.content.decode('utf-8'))

        # Delete
        del_resp = self.client.post(reverse('doctor_delete', args=[doc.pk]), follow=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertFalse(DoctorRegister.objects.filter(pk=doc.pk).exists())


