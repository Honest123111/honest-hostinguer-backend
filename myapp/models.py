from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Permission
import uuid
from django.conf import settings
from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ValidationError


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
    id = models.AutoField(primary_key=True)  # Definir explícitamente el campo id
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

    TRACKING_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]
    idmmload = models.AutoField(primary_key=True)
    origin = models.ForeignKey(
        'AddressO', on_delete=models.CASCADE, related_name='load_origin'
    )
    destiny = models.ForeignKey(
        'AddressD', on_delete=models.CASCADE, related_name='load_destiny'
    )
    equipment_type = models.CharField(max_length=100)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
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
        default='pending',
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
    )
    is_reserved = models.BooleanField(default=False)
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_loads',
    )
    tracking_status = models.CharField(
        max_length=20,
        choices=TRACKING_CHOICES,
        default='not_started',
        help_text="Status of the load's transportation",
    )
    expiration_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the load offer expires",
    )
    current_location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Current location of the load in 'latitude,longitude' format",
    )
    equipment = models.ForeignKey(
        'EquipmentType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loads',
        help_text="Required equipment for this load",
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
        ],
        default='pending',
    )
    warnings = models.ManyToManyField(
        'Warning',
        related_name='loads',
        blank=True,
        help_text="Advertencias asociadas a esta carga"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def reserve_load(self, user):
        """Reserva la carga para un usuario."""
        if self.is_reserved:
            raise ValueError("Load is already reserved.")
        self.is_reserved = True
        self.assigned_user = user
        self.save()

    def release_load(self):
        """Libera la carga, eliminando su asignación."""
        if not self.is_reserved:
            raise ValueError("Load is not reserved.")
        self.is_reserved = False
        self.assigned_user = None
        self.save()

    def update_status(self, new_status):
        """Actualiza el estado de la carga."""
        if new_status not in dict(self.STATUS_CHOICES).keys():
            raise ValidationError('Invalid status value.')
        self.status = new_status
        self.save()

    def is_expired(self):
        """Comprueba si la carga ha expirado."""
        if self.expiration_date and timezone.now() > self.expiration_date:
            return True
        return False

    def clean(self):
        """Validaciones adicionales para el modelo."""
        if self.total_weight <= 0:
            raise ValidationError('Total weight must be greater than zero.')
        if self.total_weight > 50000:  # Ejemplo de peso máximo permitido
            raise ValidationError('Total weight exceeds the maximum allowed limit.')
        if self.loaded_miles <= 0:
            raise ValidationError('Loaded miles must be greater than zero.')

    def add_warning(self, warning):
        """Agrega una advertencia a esta carga."""
        self.warnings.add(warning)

    def remove_warning(self, warning):
        """Elimina una advertencia de esta carga."""
        self.warnings.remove(warning)

    def list_warnings(self):
        """Devuelve una lista de advertencias asociadas a esta carga."""
        return self.warnings.all()

    def __str__(self):
        return f"Load {self.idmmload} - {self.status}"
    @staticmethod
    def get_active_loads():
        """Obtiene todas las cargas activas."""
        return Load.objects.filter(status__in=['pending', 'in_progress'])
    
    


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
    load = models.ForeignKey(
        'Load',
        on_delete=models.CASCADE,
        related_name='stops'
    )
    location = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    estimated_weight = models.IntegerField(validators=[validate_positive_weight])
    quantity = models.IntegerField(validators=[validate_positive_quantity])
    coordinates = models.CharField(max_length=100)
    loaded_on = models.DateTimeField(default=now, editable=False)

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

# Función de validación para asegurar que el monto de la oferta sea positivo
def validate_positive_amount(value):
    if value <= 0:
        raise ValidationError(f'{value} is not a valid amount. The amount must be positive.')

class OfferHistory(models.Model):
    id = models.AutoField(primary_key=True)  # Identificador único para cada oferta

    # Relación con el modelo Load
    load = models.ForeignKey(
        'Load',
        on_delete=models.CASCADE,
        related_name='offer_history'
    )  # Si se elimina la carga, también se eliminan las ofertas

    # Relación con el modelo de usuario
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # Si el usuario es eliminado, las ofertas asociadas también se eliminan
        related_name='offers'
    )

    # Campos específicos de la oferta
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[validate_positive_amount]
    )  # Monto de la oferta con validación para positivos
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ],
        default='pending',  # Estado inicial
    )  # Estado de la oferta
    date = models.DateTimeField(default=timezone.now)  # Fecha y hora de la oferta
    terms_change = models.BooleanField(default=False)  # Indicador de cambio en los términos

    # Fechas y horas propuestas para la operación
    proposed_pickup_date = models.DateField(null=True, blank=True)  # Fecha propuesta para recogida
    proposed_pickup_time = models.TimeField(null=True, blank=True)  # Hora propuesta para recogida
    proposed_delivery_date = models.DateField(null=True, blank=True)  # Fecha propuesta para entrega
    proposed_delivery_time = models.TimeField(null=True, blank=True)  # Hora propuesta para entrega

    # Métodos del modelo
    def accept_offer(self):
        """Aceptar la oferta y asignar la carga al usuario."""
        if self.status != 'pending':
            raise ValidationError('Only pending offers can be accepted.')

        # Asegurarse de que el monto de la oferta no sea inferior a los anteriores
        previous_accepted_offers = self.load.offer_history.filter(status='accepted')
        if previous_accepted_offers.exists() and self.amount < previous_accepted_offers.latest('date').amount:
            raise ValidationError('Offer amount cannot be lower than previously accepted offers.')

        # Reconsultar la carga para asegurar que no ha sido reservada en otro proceso
        load = self.load
        if load.is_reserved:
            raise ValidationError('This load is already reserved.')

        # Cambiar el estado de la oferta
        self.status = 'accepted'
        self.save()

        # Asignar la carga al usuario
        load.is_reserved = True
        load.assigned_user = self.user
        load.save()

    def reject_offer(self):
        """Rechazar la oferta."""
        if self.status != 'pending':
            raise ValidationError('Only pending offers can be rejected.')

        self.status = 'rejected'
        self.save()

        # Opción adicional: liberar la carga si es necesario
        # self.load.is_reserved = False
        # self.load.assigned_user = None
        # self.load.save()

    def save(self, *args, **kwargs):
        """Sobrescribir el método save para detectar cambios en los términos de la oferta."""
        if self.pk:
            # Comparar si los términos han cambiado
            original = OfferHistory.objects.get(pk=self.pk)
            if (self.amount != original.amount or 
                self.proposed_pickup_date != original.proposed_pickup_date or
                self.proposed_delivery_date != original.proposed_delivery_date):
                self.terms_change = True
        super().save(*args, **kwargs)

    def __str__(self):
        """Representación en cadena del modelo."""
        return f'Offer {self.amount} by {self.user.username} for Load {self.load.idmmload} on {self.date}'

    # Configuraciones meta del modelo
    class Meta:
        indexes = [
            models.Index(fields=['date']),  # Índice para la fecha
            models.Index(fields=['status']),  # Índice para el estado
        ]
        ordering = ['-date']  # Ordenar por fecha descendente
        verbose_name = 'Offer History'
        verbose_name_plural = 'Offer Histories'

class Job_Type(models.Model):
    idmmjob = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProcessedEmail(models.Model):
    message_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.message_id

class Warning(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    load = models.ForeignKey(
        'Load',
        on_delete=models.CASCADE,
        related_name='associated_warnings',
        null=True,  # Permitir nulos
        blank=True  # Hacer opcional en formularios
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_warnings',
        null=True,  # Permitir nulos
        blank=True  # Hacer opcional en formularios
    )

    def __str__(self):
        return self.description

    @staticmethod
    def create_default_warnings():
        """Creates predefined warnings in the database."""
        warnings = [
            "Loaded overweight",
            "Weather",
            "Hours of Service",
            "Scheduling Error",
            "Yard Congestion",
            "Driver legal break",
            "Rail delay",
            "USPS delay",
            "Relay app malfunction",
            "Relay navigation unsafe route",
            "Pallet quality issue",
            "Site badging access issue",
            "Cell service issue",
            "Driver turned away",
            "Refueling",
            "Live lift ramp"
        ]
        for warning in warnings:
            Warning.objects.get_or_create(description=warning)