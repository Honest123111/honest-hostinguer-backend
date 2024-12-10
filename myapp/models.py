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


from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

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

    def __str__(self):
        return f'{self.equipment_type} - {self.customer.name} - Priority: {self.priority}'
    
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

from django.conf import settings
from django.core.exceptions import ValidationError

class OfferHistory(models.Model):
    id = models.AutoField(primary_key=True)  # Identificador único para cada oferta
    load = models.ForeignKey(
        'Load', on_delete=models.CASCADE, related_name='offer_history'
    )  # Relación con el modelo Load
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,  # Permitir valores nulos para filas existentes
        blank=True,  # Hacerlo opcional en los formularios
        related_name='offers'
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_positive_amount]
    )  # Monto de la oferta con validación
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
    proposed_pickup_date = models.DateField(null=True, blank=True)  # Fecha propuesta para recogida
    proposed_pickup_time = models.TimeField(null=True, blank=True)  # Hora propuesta para recogida
    proposed_delivery_date = models.DateField(null=True, blank=True)  # Fecha propuesta para entrega
    proposed_delivery_time = models.TimeField(null=True, blank=True)  # Hora propuesta para entrega

    def accept_offer(self):
        """Aceptar la oferta y asignar la carga al usuario."""
        if self.status != 'pending':
            raise ValidationError('Only pending offers can be accepted.')
        if self.load.is_reserved:
            raise ValidationError('This load is already reserved.')

        # Cambiar el estado de la oferta
        self.status = 'accepted'
        self.save()

        # Asignar la carga al usuario
        self.load.is_reserved = True
        self.load.assigned_user = self.user
        self.load.save()

    def reject_offer(self):
        """Rechazar la oferta."""
        if self.status != 'pending':
            raise ValidationError('Only pending offers can be rejected.')
        self.status = 'rejected'
        self.save()

    def __str__(self):
        """Representación en cadena del modelo."""
        user_display = self.user.username if self.user else "No user"
        return f'Offer {self.amount} by {user_display} for Load {self.load.idmmload}'

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

class Warning(models.Model):
    warning_type = models.ForeignKey(
        'WarningList',
        on_delete=models.CASCADE,
        related_name='warnings',
    )
    load = models.ForeignKey(
        'Load',
        on_delete=models.CASCADE,
        related_name='associated_warnings',
        null=True,
        blank=True,
        help_text="Carga asociada a esta advertencia"
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_warnings',
        null=True,
        blank=True,
        help_text="Usuario que reportó la advertencia"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización")

    def __str__(self):
        return f"{self.warning_type.description} (Load: {self.load.idmmload if self.load else 'None'})"

    def clean(self):
        """Validaciones adicionales para el modelo."""
        if not self.load and not self.reported_by:
            raise ValidationError("A warning must be associated with either a load or a user.")

    class Meta:
        verbose_name = "Warning"
        verbose_name_plural = "Warnings"



class WarningList(models.Model):
    ISSUE_LEVEL_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]

    description = models.CharField(
        max_length=255,
        unique=True,
        help_text="Descripción del tipo de advertencia"
    )
    issue_level = models.PositiveSmallIntegerField(
        choices=ISSUE_LEVEL_CHOICES,
        default=2,
        help_text="Nivel del problema"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Indica si el tipo de advertencia está activo"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del tipo de advertencia"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización del tipo de advertencia"
    )

    def __str__(self):
        return f"{self.description} (Level: {self.get_issue_level_display()})"

    @staticmethod
    def create_default_warnings():
        """Crea advertencias predeterminadas en la lista maestra."""
        warnings = [
            ("Loaded overweight", 3),
            ("Weather", 2),
            ("Hours of Service", 2),
            ("Scheduling Error", 1),
            ("Yard Congestion", 1),
            ("Driver legal break", 2),
            ("Rail delay", 1),
            ("USPS delay", 1),
            ("Relay app malfunction", 3),
            ("Relay navigation unsafe route", 3),
            ("Pallet quality issue", 1),
            ("Site badging access issue", 1),
            ("Cell service issue", 2),
            ("Driver turned away", 3),
            ("Refueling", 1),
            ("Live lift ramp", 2),
        ]
        for description, level in warnings:
            obj, created = WarningList.objects.get_or_create(
                description=description,
                defaults={'issue_level': level, 'is_active': True}
            )
            if not created:
                obj.is_active = True  # Rehabilitar advertencias existentes si estaban desactivadas
                obj.save()

    class Meta:
        verbose_name = "Warning Type"
        verbose_name_plural = "Warning Types"