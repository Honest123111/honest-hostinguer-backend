from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db import OperationalError, ProgrammingError
from .models import CarrierUser  # Asegúrate de usar tu modelo de usuario personalizado

@receiver(post_save, sender=CarrierUser)
def add_user_to_carrier_group(sender, instance, created, **kwargs):
    """
    Agrega automáticamente un usuario de tipo Carrier al grupo "Carrier" al ser creado.
    """
    if created:  # Solo se ejecuta cuando se crea un usuario nuevo
        try:
            carrier_group, _ = Group.objects.get_or_create(name="Carrier")  # Crea o obtiene el grupo
            instance.groups.add(carrier_group)  # Asigna el grupo al usuario
        except (OperationalError, ProgrammingError):
            # La base de datos aún no está lista (migraciones no aplicadas)
            pass
