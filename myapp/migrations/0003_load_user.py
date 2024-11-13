from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def set_default_user(apps, schema_editor):
    # Obtiene el modelo Load de la aplicación
    Load = apps.get_model('myapp', 'Load')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    # Usa el primer usuario disponible como valor predeterminado
    user = User.objects.first()
    if not user:
        # Si no hay un usuario, lanza una excepción
        raise Exception("No user exists in the database. Please create at least one user.")

    # Asigna el usuario predeterminado a todos los registros de Load existentes
    for load in Load.objects.all():
        load.user = user
        load.save()

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0002_alter_customer_email'),
    ]

    operations = [
        # Añade el campo user con null=True temporalmente
        migrations.AddField(
            model_name='load',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, null=True),
        ),
        # Ejecuta la función para asignar el usuario predeterminado
        migrations.RunPython(set_default_user),
        # Luego establece user como obligatorio, eliminando null=True
        migrations.AlterField(
            model_name='load',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
