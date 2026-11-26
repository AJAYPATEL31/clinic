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

    def test_doctor_edit_view_get_prefill(self):
        """Task 1 & 2: Doctor Edit view loads prefilled form with doctor data"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        doc = DoctorRegister.objects.create(
            full_name='Sunita Rao',
            email='dr.sunita@clinicon.com',
            phone='+91 98888 77777',
            department=self.department,
            category=self.category,
            qualification='MBBS, DNB (Cardiology)',
            experience_years=12,
            consultation_fee=1200.00,
            room_number='OPD 305',
            is_active=True
        )

        edit_url = reverse('doctor_edit', args=[doc.pk])
        resp = self.client.get(edit_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'hospital/doctor_edit.html')

        content = resp.content.decode('utf-8')
        # Check prefilled values in HTML form
        self.assertIn('Sunita Rao', content)
        self.assertIn('dr.sunita@clinicon.com', content)
        self.assertIn('+91 98888 77777', content)
        self.assertIn('MBBS, DNB (Cardiology)', content)
        self.assertIn('1200', content)
        self.assertIn('OPD 305', content)
        self.assertIn('Edit Doctor - Dr. Sunita Rao', content)

    def test_doctor_edit_view_post_update(self):
        """Task 2: Doctor Edit view successfully updates doctor details"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        doc = DoctorRegister.objects.create(
            full_name='Manoj Verma',
            email='dr.manoj@clinicon.com',
            phone='+91 97777 66666',
            department=self.department,
            category=self.category,
            qualification='MBBS',
            experience_years=5,
            consultation_fee=600.00,
            room_number='OPD 102',
            is_active=True
        )

        edit_url = reverse('doctor_edit', args=[doc.pk])
        update_data = {
            'full_name': 'Manoj K. Verma',
            'email': 'dr.manoj.updated@clinicon.com',
            'phone': '+91 97777 88888',
            'department': self.department.id,
            'category': self.category.id,
            'qualification': 'MBBS, MD (Medicine)',
            'experience_years': 7,
            'consultation_fee': '850.00',
            'room_number': 'OPD 204',
            'address': 'Senior Doctors Block A',
            'is_active': True,
        }

        resp = self.client.post(edit_url, update_data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'hospital/doctor_list.html')

        # Check DB update
        doc.refresh_from_db()
        self.assertEqual(doc.full_name, 'Manoj K. Verma')
        self.assertEqual(doc.email, 'dr.manoj.updated@clinicon.com')
        self.assertEqual(doc.phone, '+91 97777 88888')
        self.assertEqual(doc.qualification, 'MBBS, MD (Medicine)')
        self.assertEqual(doc.experience_years, 7)
        self.assertEqual(float(doc.consultation_fee), 850.00)
        self.assertEqual(doc.room_number, 'OPD 204')

    def test_doctor_confirm_delete_get_view(self):
        """Task 3: Doctor Delete GET view renders confirmation page with doctor info"""
        self.client.login(username=self.admin_email, password=self.admin_password)
        doc = DoctorRegister.objects.create(
            full_name='Ramesh Dave',
            email='dr.ramesh@clinicon.com',
            phone='+91 94444 33333',
            department=self.department,
            category=self.category,
            qualification='MBBS, MS',
            experience_years=9,
            consultation_fee=800.00
        )

        del_url = reverse('doctor_delete', args=[doc.pk])
        resp = self.client.get(del_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'hospital/doctor_confirm_delete.html')
        content = resp.content.decode('utf-8')
        self.assertIn('Ramesh Dave', content)
        self.assertIn('Confirm Doctor Removal', content)
        self.assertIn('Cardiology', content)

    # ----------------------------------------------------
    # Today's Tasks Tests:
    # 1. Pagination & Search on Doctor List
    # 2. Authenticated Admin User Access Restrictions
    # 3. User / Admin Registration HTML Page & Form Handling
    # ----------------------------------------------------

    def test_doctor_pagination_and_search(self):
        """Task 1: Pagination and search on doctor listing view and HTML page"""
        self.client.login(username=self.admin_email, password=self.admin_password)

        # Create 8 doctors to test pagination (default 6 per page)
        doctors = []
        for i in range(1, 9):
            doctors.append(DoctorRegister(
                full_name=f'Doctor Number {i}',
                email=f'doc{i}@clinicon.com',
                phone=f'+91 90000 0000{i}',
                department=self.department,
                category=self.category,
                qualification=f'MBBS {i}',
                experience_years=i,
                consultation_fee=500.00 + (i * 50)
            ))
        DoctorRegister.objects.bulk_create(doctors)

        # Page 1
        resp_p1 = self.client.get(reverse('doctor_list'))
        self.assertEqual(resp_p1.status_code, 200)
        self.assertTrue(resp_p1.context['is_paginated'])
        self.assertEqual(len(resp_p1.context['doctors']), 6)
        self.assertEqual(resp_p1.context['page_obj'].number, 1)
        self.assertEqual(resp_p1.context['paginator'].num_pages, 2)
        content_p1 = resp_p1.content.decode('utf-8')
        self.assertIn('Page', content_p1)
        self.assertIn('pagination', content_p1)

        # Page 2
        resp_p2 = self.client.get(reverse('doctor_list') + '?page=2')
        self.assertEqual(resp_p2.status_code, 200)
        self.assertEqual(len(resp_p2.context['doctors']), 2)
        self.assertEqual(resp_p2.context['page_obj'].number, 2)

        # Search filter
        search_resp = self.client.get(reverse('doctor_list') + '?q=Doctor Number 3')
        self.assertEqual(search_resp.status_code, 200)
        self.assertEqual(search_resp.context['total_doctors'], 1)
        self.assertIn('Doctor Number 3', search_resp.content.decode('utf-8'))

    def test_admin_access_restrictions(self):
        """Task 2: Restrict access to authenticated admin users in views and HTML"""
        # 1. Unauthenticated access should redirect to login
        anon_resp = self.client.get(reverse('doctor_register'))
        self.assertEqual(anon_resp.status_code, 302)
        self.assertIn('/login/', anon_resp.url)

        # 2. Authenticated non-admin staff user should get 403 Forbidden with access_denied page
        staff_user = CustomUser.objects.create_user(
            email='staffmember@clinicon.com',
            password='staffpassword123',
            role='Staff',
            is_staff=False,
            is_superuser=False
        )
        self.client.login(username='staffmember@clinicon.com', password='staffpassword123')

        restricted_resp = self.client.get(reverse('doctor_register'))
        self.assertEqual(restricted_resp.status_code, 403)
        self.assertTemplateUsed(restricted_resp, 'hospital/access_denied.html')
        self.assertIn('Administrator Privileges Required', restricted_resp.content.decode('utf-8'))

        # Also restricted on dashboard
        dash_resp = self.client.get(reverse('dashboard'))
        self.assertEqual(dash_resp.status_code, 403)

        # 3. Authenticated admin user should have full access (200 OK)
        self.client.login(username=self.admin_email, password=self.admin_password)
        admin_resp = self.client.get(reverse('doctor_register'))
        self.assertEqual(admin_resp.status_code, 200)

    def test_user_registration_page_get_and_post(self):
        """Task 3: Registration HTML page with proper fields and form handling"""
        # GET registration page
        get_resp = self.client.get(reverse('register'))
        self.assertEqual(get_resp.status_code, 200)
        self.assertTemplateUsed(get_resp, 'hospital/register.html')
        content = get_resp.content.decode('utf-8')

        # Check required fields exist in HTML
        self.assertIn('name="full_name"', content)
        self.assertIn('name="email"', content)
        self.assertIn('name="contact_number"', content)
        self.assertIn('name="role"', content)
        self.assertIn('name="department_name"', content)
        self.assertIn('name="password"', content)
        self.assertIn('name="confirm_password"', content)

        # POST valid registration
        post_resp = self.client.post(reverse('register'), {
            'full_name': 'Dr. Alok Verma',
            'email': 'dr.alok@clinicon.com',
            'contact_number': '+91 98888 12345',
            'department_name': 'Neurology',
            'role': 'Admin',
            'password': 'securepassword123',
            'confirm_password': 'securepassword123',
        }, follow=True)

        self.assertEqual(post_resp.status_code, 200)
        # Should redirect to login page with success message
        self.assertTemplateUsed(post_resp, 'hospital/login.html')
        self.assertIn('Registration successful', post_resp.content.decode('utf-8'))

        # Verify user and registration record in database
        new_user = CustomUser.objects.filter(email='dr.alok@clinicon.com').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.role, 'Admin')
        self.assertTrue(new_user.is_staff)
        self.assertTrue(UserRegistration.objects.filter(email='dr.alok@clinicon.com').exists())

        # POST with password mismatch
        mismatch_resp = self.client.post(reverse('register'), {
            'full_name': 'Mismatched User',
            'email': 'mismatch@clinicon.com',
            'contact_number': '+91 98888 99999',
            'department_name': 'Administration',
            'role': 'Staff',
            'password': 'password123',
            'confirm_password': 'differentpassword',
        })
        self.assertEqual(mismatch_resp.status_code, 200)
        self.assertIn('Passwords do not match', mismatch_resp.content.decode('utf-8'))
        self.assertFalse(CustomUser.objects.filter(email='mismatch@clinicon.com').exists())




