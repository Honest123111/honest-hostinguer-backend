from django import forms
from django.contrib.auth.forms import UserCreationForm
from myapp.models import CarrierUser, CarrierEmployeeProfile

class CarrierEmployeeRegisterForm(UserCreationForm):
    position = forms.ChoiceField(choices=CarrierEmployeeProfile.POSITION_CHOICES)
    phone_number = forms.CharField()
    extension = forms.CharField(required=False)

    class Meta:
        model = CarrierUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'position', 'phone_number', 'extension']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'carrier_employee'
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Creamos el perfil del empleado del carrier
            CarrierEmployeeProfile.objects.create(
                user=user,
                position=self.cleaned_data['position'],
                phone_number=self.cleaned_data['phone_number'],
                extension=self.cleaned_data.get('extension')
            )
        return user
