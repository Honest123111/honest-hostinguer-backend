from django.db import models
from django.utils import timezone


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


class Stop(models.Model):
    id = models.AutoField(primary_key=True)
    load = models.ForeignKey(Load, on_delete=models.CASCADE, related_name='stops')
    location = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    action_type = models.CharField(max_length=50)
    estimated_weight = models.IntegerField()
    quantity = models.IntegerField()
    loaded_on = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.location} - {self.action_type}'


class EquipmentType(models.Model):
    idmmequipment = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Job_Type(models.Model):
    idmmjob = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class OfferHistory(models.Model):
    id = models.AutoField(primary_key=True)
    load = models.ForeignKey(Load, on_delete=models.CASCADE, related_name='offer_history')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    date = models.DateTimeField(default=timezone.now)
    terms_change = models.BooleanField(default=False)
    proposed_pickup_date = models.DateField(null=True, blank=True)
    proposed_pickup_time = models.TimeField(null=True, blank=True)
    proposed_delivery_date = models.DateField(null=True, blank=True)
    proposed_delivery_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'Offer {self.amount} for {self.load}'


class ProcessedEmail(models.Model):
    message_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.message_id
