from django.core.management.base import BaseCommand
from hospital.models import CustomUser, UserRegistration
import getpass


class Command(BaseCommand):
    help = 'Create or update a Superuser with specific Email and Password'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Admin email address')
        parser.add_argument('--password', type=str, help='Admin password')
        parser.add_argument('--name', type=str, default='Administrator', help='Admin full name')

    def handle(self, *args, **options):
        email = options.get('email')
        password = options.get('password')
        name = options.get('name', 'Administrator')

        if not email:
            email = input('Enter Admin Email: ').strip()
        if not password:
            password = getpass.getpass('Enter Admin Password: ').strip()

        if not email or not password:
            self.stderr.write(self.style.ERROR('Email and password cannot be empty!'))
            return

        email = email.lower().strip()
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': name,
                'is_staff': True,
                'is_superuser': True,
                'role': 'Admin',
                'is_active': True,
            }
        )

        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.role = 'Admin'
        user.is_active = True
        user.save()

        UserRegistration.objects.update_or_create(
            user=user,
            defaults={
                'full_name': name,
                'email': email,
                'department_name': 'Hospital Administration',
                'is_active': True,
            }
        )

        status_str = "Created new" if created else "Updated existing"
        self.stdout.write(self.style.SUCCESS(f"\n[SUCCESS] {status_str} Superuser:"))
        self.stdout.write(self.style.SUCCESS(f"  • Email    : {email}"))
        self.stdout.write(self.style.SUCCESS(f"  • Password : (Securely encrypted in database)"))
        self.stdout.write(self.style.SUCCESS("Ab admin login page par yahi email aur password dalne par hi login hoga!\n"))
