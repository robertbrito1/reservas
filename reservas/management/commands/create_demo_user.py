import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# Usuario público para que cualquiera pueda probar la demo (aparece en el README).
# No es staff ni superusuario: puede usar el panel de reservas, pero no entrar en /admin.
DEMO_USERNAME = "demo"
DEMO_PASSWORD_POR_DEFECTO = "demo-reservas"


class Command(BaseCommand):
    help = "Crea o actualiza el usuario de demostración (sin permisos de administrador)"

    def handle(self, *args, **options):
        password = os.environ.get("DJANGO_DEMO_PASSWORD", DEMO_PASSWORD_POR_DEFECTO)

        user, created = User.objects.get_or_create(username=DEMO_USERNAME)
        user.is_staff = False
        user.is_superuser = False
        user.is_active = True
        user.set_password(password)
        user.save()

        accion = "creado" if created else "actualizado"
        self.stdout.write(self.style.SUCCESS(f"✓ Usuario demo '{DEMO_USERNAME}' {accion}"))
