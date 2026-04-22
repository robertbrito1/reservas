import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update superuser from env vars or defaults"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default=os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin"),
            help="Superuser username",
        )
        parser.add_argument(
            "--email",
            type=str,
            default=os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com"),
            help="Superuser email",
        )
        parser.add_argument(
            "--password",
            type=str,
            default=os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123"),
            help="Superuser password",
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Superuser '{username}' created successfully")
            )
        else:
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Superuser '{username}' updated successfully")
            )
