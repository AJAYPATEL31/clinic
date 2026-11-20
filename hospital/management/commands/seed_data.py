from django.core.management.base import BaseCommand
from hospital.models import CustomUser, UserRegistration, Department, DoctorCategory


class Command(BaseCommand):
    help = 'Seed database with default admin user, departments, and doctor categories for Clinic On'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting database seed for Clinic On...'))

        # 1. Create or update Default Admin
        admin_email = 'admin@clinicon.com'
        admin_password = 'admin123'
        user, created = CustomUser.objects.get_or_create(
            email=admin_email,
            defaults={
                'username': admin_email,
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'Admin',
                'is_staff': True,
                'is_superuser': True,
                'phone': '+91 98765 43210',
            }
        )
        if created:
            user.set_password(admin_password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created Admin Superuser: {admin_email} / {admin_password}'))
        else:
            user.set_password(admin_password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Admin Superuser: {admin_email} / {admin_password}'))

        # 2. Create UserRegistration record (Day 2 requirement)
        reg_record, reg_created = UserRegistration.objects.get_or_create(
            user=user,
            defaults={
                'full_name': 'System Administrator',
                'email': admin_email,
                'contact_number': '+91 98765 43210',
                'department_name': 'Hospital Administration',
                'is_active': True,
            }
        )
        if reg_created:
            self.stdout.write(self.style.SUCCESS('Created UserRegistration record for Admin'))

        # 3. Create Sample Departments (Day 2 requirement)
        departments_data = [
            {
                'name': 'Cardiology',
                'code': 'CARD-01',
                'head_of_department': 'Dr. Rajesh Sharma',
                'description': 'Heart health, coronary artery disease, arrhythmia, and cardiovascular interventions.',
            },
            {
                'name': 'Neurology',
                'code': 'NEUR-01',
                'head_of_department': 'Dr. Priya Nair',
                'description': 'Diagnosis and treatment of nervous system disorders and neurological conditions.',
            },
            {
                'name': 'Pediatrics',
                'code': 'PED-01',
                'head_of_department': 'Dr. Amit Patel',
                'description': 'Comprehensive medical care for infants, children, and adolescents.',
            },
            {
                'name': 'Orthopedics',
                'code': 'ORTH-01',
                'head_of_department': 'Dr. Sunita Rao',
                'description': 'Musculoskeletal system surgery, joint replacements, and bone trauma care.',
            },
            {
                'name': 'General Medicine',
                'code': 'GM-01',
                'head_of_department': 'Dr. Vikram Deshmukh',
                'description': 'Primary healthcare, preventive medicine, diagnosis and adult medical treatments.',
            },
        ]

        dept_objs = {}
        for d in departments_data:
            dept, _ = Department.objects.get_or_create(
                name=d['name'],
                defaults={
                    'code': d['code'],
                    'head_of_department': d['head_of_department'],
                    'description': d['description'],
                    'is_active': True,
                }
            )
            dept_objs[dept.name] = dept

        self.stdout.write(self.style.SUCCESS(f'Configured {len(dept_objs)} Hospital Departments.'))

        # 4. Create Sample Doctor Categories (Day 3 requirement)
        categories_data = [
            {
                'name': 'Senior Consultant Cardiologist',
                'department': dept_objs['Cardiology'],
                'consultation_fee': 1000.00,
                'description': 'Senior specialist with 15+ years experience in complex heart ailments and angiography.',
            },
            {
                'name': 'Interventional Cardiologist',
                'department': dept_objs['Cardiology'],
                'consultation_fee': 1200.00,
                'description': 'Catheter-based treatments for heart diseases, stenting, and angioplasty.',
            },
            {
                'name': 'Senior Neurosurgeon',
                'department': dept_objs['Neurology'],
                'consultation_fee': 1500.00,
                'description': 'Brain and spinal surgery specialist for neuro-trauma and cerebrovascular disorders.',
            },
            {
                'name': 'Resident Neurologist',
                'department': dept_objs['Neurology'],
                'consultation_fee': 750.00,
                'description': 'In-hospital acute care and treatment for migraines, neuropathy, and epilepsy.',
            },
            {
                'name': 'Senior Pediatric Specialist',
                'department': dept_objs['Pediatrics'],
                'consultation_fee': 600.00,
                'description': 'Pediatric intensive care, immunizations, and developmental medicine.',
            },
            {
                'name': 'Orthopedic Surgeon & Specialist',
                'department': dept_objs['Orthopedics'],
                'consultation_fee': 900.00,
                'description': 'Joint replacement surgery, sports injury rehabilitation, and spine treatment.',
            },
            {
                'name': 'General Physician',
                'department': dept_objs['General Medicine'],
                'consultation_fee': 500.00,
                'description': 'Outpatient consultations for common fevers, infections, diabetes, and hypertension.',
            },
        ]

        created_cat_count = 0
        for c in categories_data:
            _, created = DoctorCategory.objects.get_or_create(
                name=c['name'],
                department=c['department'],
                defaults={
                    'consultation_fee': c['consultation_fee'],
                    'description': c['description'],
                    'is_active': True,
                }
            )
            if created:
                created_cat_count += 1

        self.stdout.write(self.style.SUCCESS(f'Configured Doctor Categories (total: {DoctorCategory.objects.count()}).'))
        self.stdout.write(self.style.SUCCESS('\n=== Seed Completed Successfully! ==='))
        self.stdout.write(self.style.SUCCESS('Admin Login: admin@clinicon.com / admin123'))
