from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Permission
import uuid

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Nombre único del rol
    permissions = models.ManyToManyField(Permission, blank=True)  # Relación con permisos

    def __str__(self):
        return self.name

class CarrierUser(AbstractUser):
    CARRIER_TYPES = [
        ('us', 'United States-based Carrier'),
        ('international', 'International Carrier'),
    ]
    carrier_type = models.CharField(max_length=20, choices=CARRIER_TYPES, default='us')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    DOT_number = models.CharField(max_length=20, blank=True, null=True)
    license_guid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Ajustar related_name para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='carrieruser_groups',  # Cambiar el related_name
        blank=True,
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='carrieruser_permissions',  # Cambiar el related_name
        blank=True,
        help_text='Specific permissions for this user.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.carrier_type}"

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    corporation = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    dotnumber = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class AddressO(models.Model):
    id = models.AutoField(primary_key=True)
    zip_code = models.IntegerField()
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='origin_addresses', null=True, blank=True
    )

    def __str__(self):
        return self.address


class AddressD(models.Model):
    id = models.AutoField(primary_key=True)
    zip_code = models.IntegerField()
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='destination_addresses', null=True, blank=True
    )

    def __str__(self):
        return self.address


class Load(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    idmmload = models.AutoField(primary_key=True)
    origin = models.ForeignKey(AddressO, on_delete=models.CASCADE, related_name='load_origin')
    destiny = models.ForeignKey(AddressD, on_delete=models.CASCADE, related_name='load_destiny')
    equipment_type = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loaded_miles = models.IntegerField()
    total_weight = models.IntegerField()
    commodity = models.CharField(max_length=100)
    classifications_and_certifications = models.CharField(max_length=255)
    offer = models.DecimalField(max_digits=10, decimal_places=2)
    is_offerted = models.BooleanField(default=False)
    number_of_offers = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',  # Estado predeterminado
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',  # Prioridad por defecto es 'medium'
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática
    updated_at = models.DateTimeField(auto_now=True)  # Fecha de última actualización automática

    def __str__(self):
        return f'{self.equipment_type} - {self.customer.name} - Priority: {self.priority}'


from django.db import models
from django.core.exceptions import ValidationError

# Opciones para el tipo de acción
ACTION_CHOICES = [
    ('live_load', 'Live Load'),
    ('dropped_trailer', 'Dropped Trailer'),
    ('other', 'Other'),
    ('delivery', 'Delivery'),  # Nueva opción: Delivery
    ('pickup', 'Pickup'),      # Nueva opción: Pickup
]

# Función de validación para peso positivo
def validate_positive_weight(value):
    if value <= 0:
        raise ValidationError('Estimated weight must be positive.')

# Función de validación para cantidad positiva
def validate_positive_quantity(value):
    if value <= 0:
        raise ValidationError('Quantity must be positive.')

class Stop(models.Model):
    id = models.AutoField(primary_key=True)
    load = models.ForeignKey('Load', on_delete=models.CASCADE, related_name='stops')
    location = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    estimated_weight = models.IntegerField(validators=[validate_positive_weight])  # Validación de peso positivo
    quantity = models.IntegerField(validators=[validate_positive_quantity])  # Validación de cantidad positiva
    loaded_on = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=100)  # Usamos coordenadas como cadena por ahora

    def __str__(self):
        return f'{self.location} - {self.action_type}'

class EquipmentType(models.Model):
    idmmequipment = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Opciones posibles para el estado de la oferta
OFFER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]

# Función de validación para asegurar que el monto de la oferta sea positivo
def validate_positive_amount(value):
    if value <= 0:
        raise ValidationError(f'{value} is not a valid amount. The amount must be positive.')

class OfferHistory(models.Model):
    id = models.AutoField(primary_key=True)  # Identificador único para cada oferta
    load = models.ForeignKey(Load, on_delete=models.CASCADE, related_name='offer_history')  # Relación con el modelo Load
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive_amount])  # Monto de la oferta con validación
    status = models.CharField(max_length=50, choices=OFFER_STATUS_CHOICES)  # Estado de la oferta
    date = models.DateTimeField(default=timezone.now)  # Fecha y hora de la oferta
    terms_change = models.BooleanField(default=False)  # Indicador de cambio en los términos
    proposed_pickup_date = models.DateField(null=True, blank=True)  # Fecha propuesta para recogida
    proposed_pickup_time = models.TimeField(null=True, blank=True)  # Hora propuesta para recogida
    proposed_delivery_date = models.DateField(null=True, blank=True)  # Fecha propuesta para entrega
    proposed_delivery_time = models.TimeField(null=True, blank=True)  # Hora propuesta para entrega

    def __str__(self):
        return f'Offer {self.amount} for {self.load}'

    # Configuración de los índices para optimizar las consultas
    class Meta:
        indexes = [
            models.Index(fields=['date']),  # Índice para la fecha
            models.Index(fields=['status']),  # Índice para el estado
        ]

class Job_Type(models.Model):
    idmmjob = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProcessedEmail(models.Model):
    message_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.message_id
