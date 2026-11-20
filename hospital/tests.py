from django.test import TestCase, Client
from django.urls import reverse
from hospital.models import CustomUser, UserRegistration, LoginLog, Department, DoctorCategory


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
