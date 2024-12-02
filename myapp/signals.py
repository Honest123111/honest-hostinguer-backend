from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CarrierUser  # Asegúrate de usar tu modelo de usuario personalizado

@receiver(post_save, sender=CarrierUser)
def add_user_to_carrier_group(sender, instance, created, **kwargs):
    if created:  # Solo se ejecuta cuando se crea un usuario
        carrier_group, _ = Group.objects.get_or_create(name="Carrier")  # Crea el grupo si no existe
        instance.groups.add(carrier_group)  # Asigna el grupo al usuario
