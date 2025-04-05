from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Permission , Group
import uuid
from django.conf import settings
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from decimal import Decimal


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

    id = models.AutoField(primary_key=True)
    carrier_type = models.CharField(max_length=20, choices=CARRIER_TYPES, default='us')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    DOT_number = models.CharField(max_length=20, blank=True, null=True)
    license_guid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    number_of_trucks = models.PositiveIntegerField(default=0, help_text="Number of trucks owned by the carrier")

    groups = models.ManyToManyField(
        Group,
        related_name='carrieruser_groups',
        blank=True,
        help_text='The single group this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='carrieruser_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} - {self.carrier_type}"

    def update_user(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return self

    def delete_user(self):
        self.delete()

    def verify_password(self, raw_password):
        return self.check_password(raw_password)

    @property
    def is_carrier_employee(self):
        return self.groups.filter(name="Carrier Employee").exists()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # ⚠️ Verificar si hay más de un grupo y limpiar
        if self.groups.count() > 1:
            first_group = self.groups.first()
            self.groups.set([first_group])  # Reemplaza todos por el primero

class CarrierEmployeeProfile(models.Model):
    POSITION_CHOICES = [
        ('employee', 'Employee'),
        ('driver', 'Driver'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carrier_profile')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    creation_date = models.DateField(auto_now_add=True)
    phone_number = models.CharField(max_length=20)
    extension = models.CharField(max_length=10, blank=True, null=True)

    # Campos del sistema
    carrier_employee_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, default='Active')
    start_date = models.DateField(default=timezone.now)
    termination_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.position}"


class Corporation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    dot_number = models.CharField(max_length=100, null=True, blank=True)  # si aplica
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Customer(models.Model):
    corporation = models.ForeignKey(Corporation, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    position = models.CharField(max_length=100)  # Ej: Logística, Encargado de pagos, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.position}) - {self.corporation.name}"


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
    is_closed = models.BooleanField(default=False, help_text="Indicates if the load is closed.")
    equipment_type = models.CharField(max_length=100)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    loaded_miles = models.IntegerField(null=True, blank=True)
    total_weight = models.IntegerField(null=True, blank=True)
    commodity = models.CharField(max_length=100)
    classifications_and_certifications = models.CharField(max_length=255)
    offer = models.DecimalField(max_digits=10, decimal_places=2,default=0)
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
    honest_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True,
        help_text="ID proveniente de un correo de truck availability u otra fuente"
    )
    under_review = models.BooleanField(
        default=False,
        help_text="Indica si la carga está en revisión y no se muestra hasta que sea aprobada."
    )
    def save(self, *args, **kwargs):
        if self.honest_id and self.honest_id.strip():  # Si honest_id no está vacío
            existing_load = Load.objects.filter(honest_id=self.honest_id).exclude(idmmload=self.idmmload).first()
            if existing_load:
              raise ValidationError(f"El honest_id '{self.honest_id}' ya está en uso en otra carga.")

        super().save(*args, **kwargs)
        
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
       
        if self.assigned_user:
            # Obtener la cantidad de cargas asignadas en estado pending o in_progress
            assigned_loads_count = Load.objects.filter(
                assigned_user=self.assigned_user,
                status__in=['pending', 'in_progress']
            ).count()

            # Comparar con la cantidad de camiones que posee el usuario
            if assigned_loads_count >= self.assigned_user.trucks.count():
                raise ValidationError(
                    "The user cannot be assigned more loads than the number of trucks they own."
                )


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
    id = models.AutoField(primary_key=True)  # ✅ Identificador único explícito
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
def validate_positive_amount(value):
    if value <= 0:
        raise ValidationError(f'{value} is not a valid amount. The amount must be positive.')

class OfferHistory(models.Model):
    id = models.AutoField(primary_key=True)

    # Relación con el modelo Load
    load = models.ForeignKey(
        'Load',
        on_delete=models.CASCADE,
        related_name='offer_history'
    )

    # Relación con el usuario autenticado
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers'
    )

    # Campos específicos de la oferta
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
    )
    date = models.DateTimeField(default=timezone.now)
    terms_change = models.BooleanField(default=False)

    # Fechas y horas propuestas
    proposed_pickup_date = models.DateField(null=True, blank=True)
    proposed_pickup_time = models.TimeField(null=True, blank=True)
    proposed_delivery_date = models.DateField(null=True, blank=True)
    proposed_delivery_time = models.TimeField(null=True, blank=True)

    def accept_offer(self):
        """Aceptar la oferta y asignar la carga al usuario."""
        if self.status != 'pending':
            raise ValidationError('Only pending offers can be accepted.')

        previous_accepted_offers = self.load.offer_history.filter(status='accepted')
        if previous_accepted_offers.exists() and self.amount < previous_accepted_offers.latest('date').amount:
            raise ValidationError('Offer amount cannot be lower than previously accepted offers.')

        if self.load.is_reserved:
            raise ValidationError('This load is already reserved.')

        self.status = 'accepted'
        self.save()

        self.load.is_reserved = True
        self.load.assigned_user = self.user
        self.load.save()

    def reject_offer(self):
        """Rechazar la oferta."""
        if self.status != 'pending':
            raise ValidationError('Only pending offers can be rejected.')

        self.status = 'rejected'
        self.save()

    def save(self, *args, **kwargs):
        """Sobrescribe el método save para validar cambios y decimales."""
        if self.pk:
            try:
                original = OfferHistory.objects.get(pk=self.pk)
                if (
                    self.amount != original.amount or
                    getattr(self, 'proposed_pickup_date', None) != getattr(original, 'proposed_pickup_date', None) or
                    getattr(self, 'proposed_delivery_date', None) != getattr(original, 'proposed_delivery_date', None)
                ):
                    self.terms_change = True
            except OfferHistory.DoesNotExist:
                pass

        if isinstance(self.amount, float):
            self.amount = Decimal(str(self.amount))

        # ⚠️ Solo ejecutar esto si 'offer' realmente existe en el modelo Load
        if hasattr(self.load, 'offer') and isinstance(self.load.offer, float):
            self.load.offer = Decimal(str(self.load.offer))

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Offer {self.amount} by User {self.user.id} for Load {self.load.idmmload} on {self.date}'

    @classmethod
    def assign_load_without_offer(cls, load, user):
        """Asigna una carga a un usuario sin crear una oferta."""
        if load.is_reserved:
            raise ValidationError('This load is already reserved.')

        load.is_reserved = True
        load.assigned_user = user
        load.save()

        return f'Load {load.id} has been assigned to user ID {user.id} without an offer.'

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
        ordering = ['-date']
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
            ("Honest app malfunction", 3),
            ("Honest navigation unsafe route", 3),
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


class LoadProgress(models.Model):
    idmmload = models.ForeignKey('Load', on_delete=models.CASCADE, related_name='progress')
    coordinates = models.CharField(max_length=255)
    step = models.CharField(max_length=255)
    pending_for_approval = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=now)
    picture = models.ImageField(upload_to='progress_pictures/')

    def __str__(self):
        return f"Progress for Load {self.idmmload.idmmload} - Step: {self.step}"

class Truck(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trucks')
    plate_number = models.CharField(max_length=20, unique=True, help_text="Truck license plate")
    model = models.CharField(max_length=50, help_text="Truck model")
    equipment_type = models.ForeignKey(
        'EquipmentType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Type of equipment the truck is compatible with"
    )

    def __str__(self):
        return f"{self.plate_number} - {self.model}"

class UserPermission(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    allowed_views = models.JSONField(default=list, help_text="Lista de vistas permitidas para este usuario")

    def __str__(self):
        return f"Permissions for {self.user.username}"

class Delay(models.Model):
    # Relación con el modelo Stop
    stop = models.ForeignKey(
        'Stop', 
        on_delete=models.CASCADE, 
        related_name='delays'
    )  # Si se elimina el Stop, también se eliminan los delays

    # Opciones para estado de salida del stop
    ON_TIME = 'on_time'
    DELAYED = 'delayed'
    ISSUE = 'issue'

    STOP_STATUS_CHOICES = [
        (ON_TIME, 'On Time'),
        (DELAYED, 'Delayed'),
        (ISSUE, 'Issue at Stop'),
    ]

    stop_status = models.CharField(
        max_length=20,
        choices=STOP_STATUS_CHOICES,
        default=ON_TIME
    )

    # Opciones para el tipo de retraso
    DELAY_REASON_CHOICES = [
        ('traffic', 'Traffic'),
        ('weather', 'Weather Conditions'),
        ('mechanical', 'Mechanical Failure'),
        ('loading', 'Loading Issues'),
        ('unloading', 'Unloading Issues'),
        ('route_change', 'Route Change'),
        ('inspection', 'Inspection Delay'),
        ('other', 'Other'),
    ]

    delay_reason = models.CharField(
        max_length=50,
        choices=DELAY_REASON_CHOICES,
        null=True,
        blank=True
    )

    # Tiempo estimado de retraso en minutos
    estimated_delay_time = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated delay time in minutes"
    )

    # Fecha y hora estimada de llegada
    estimated_arrival = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Estimated arrival date and time"
    )

    created_at = models.DateTimeField(default=now, editable=False)  # Fecha de registro automática

    def __str__(self):
        return f"Delay at Stop {self.stop.id}: {self.get_stop_status_display()} - {self.get_delay_reason_display()} ({self.estimated_delay_time} min, ETA: {self.estimated_arrival})"

    class Meta:
        indexes = [
            models.Index(fields=['stop_status']),  # Índice en el estado de salida del stop
            models.Index(fields=['delay_reason']),  # Índice en el tipo de retraso
        ]
        ordering = ['-created_at']  # Ordenar por fecha descendente
        verbose_name = "Delay"
        verbose_name_plural = "Delays"
