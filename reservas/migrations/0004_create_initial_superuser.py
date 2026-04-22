import os

from django.conf import settings
from django.db import migrations


def create_initial_superuser(apps, schema_editor):
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    # Skip safely when deployment secrets are not configured.
    if not username or not email or not password:
        return

    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    UserModel = apps.get_model(app_label, model_name)
    db_alias = schema_editor.connection.alias

    user, created = UserModel.objects.using(db_alias).get_or_create(
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
        user.save(using=db_alias)
        return

    changed = False
    if user.email != email:
        user.email = email
        changed = True
    if not user.is_staff:
        user.is_staff = True
        changed = True
    if not user.is_superuser:
        user.is_superuser = True
        changed = True
    if not user.is_active:
        user.is_active = True
        changed = True

    # Keep password synchronized with deployment secret when it changes.
    if password and not user.check_password(password):
        user.set_password(password)
        changed = True

    if changed:
        user.save(using=db_alias)


class Migration(migrations.Migration):

    dependencies = [
        ("reservas", "0003_reserva_personas"),
    ]

    operations = [
        migrations.RunPython(create_initial_superuser, migrations.RunPython.noop),
    ]