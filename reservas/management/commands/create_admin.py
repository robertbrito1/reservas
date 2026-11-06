import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea o actualiza el superusuario a partir de variables de entorno"

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        # Sin contraseña definida no se crea nada: así nunca hay un admin con una contraseña por defecto.
        if not password:
            self.stdout.write(
                self.style.WARNING("DJANGO_SUPERUSER_PASSWORD no está definida: no se crea el superusuario.")
            )
            return

        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        accion = "creado" if created else "actualizado"
        self.stdout.write(self.style.SUCCESS(f"✓ Superusuario '{username}' {accion}"))
