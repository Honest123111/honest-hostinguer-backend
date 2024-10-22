from django.db import models

class AddressO(models.Model):
    zip_code = models.IntegerField()
    address = models.CharField(max_length=255)
    state = models.IntegerField()
    coordinates = models.CharField(max_length=255)

    def __str__(self):
        return self.address

class AddressD(models.Model):
    zip_code = models.IntegerField()
    address = models.CharField(max_length=255)
    state = models.IntegerField()
    coordinates = models.CharField(max_length=255)

    def __str__(self):
        return self.address

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.ForeignKey(AddressO, on_delete=models.CASCADE)  # Link to AddressO
    corporation = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Load(models.Model):
    origin = models.ForeignKey(AddressO, on_delete=models.CASCADE, related_name='load_origin')
    destiny = models.ForeignKey(AddressD, on_delete=models.CASCADE, related_name='load_destiny')
    equipment_type = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.equipment_type} - {self.customer.name}'
