from django.db import models

class Customer(models.Model):
    id = models.AutoField(primary_key=True)  # Clave primaria
    name = models.CharField(max_length=100)
    email = models.EmailField()
    corporation = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    dotnumber = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class AddressO(models.Model):
    id = models.AutoField(primary_key=True)  # Clave primaria
    zip_code = models.IntegerField()
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='origin_addresses', null=True, blank=True)  # Relación con Customer

    def __str__(self):
        return self.address


class AddressD(models.Model):
    id = models.AutoField(primary_key=True)  # Clave primaria
    zip_code = models.IntegerField()
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='destination_addresses', null=True, blank=True)  # Relación con Customer

    def __str__(self):
        return self.address


class Load(models.Model):
    idmmload = models.AutoField(primary_key=True)  # Clave primaria
    origin = models.ForeignKey(AddressO, on_delete=models.CASCADE, related_name='load_origin')
    destiny = models.ForeignKey(AddressD, on_delete=models.CASCADE, related_name='load_destiny')
    equipment_type = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Relación con Customer
    loaded_miles = models.IntegerField()
    total_weight = models.IntegerField()
    commodity = models.CharField(max_length=100)
    classifications_and_certifications = models.CharField(max_length=255)
    offer = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.equipment_type} - {self.customer.name}'


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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='stops', null=True, blank=True)  # Relación con Customer

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
