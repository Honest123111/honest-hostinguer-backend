from django import forms
from django.contrib.auth.forms import UserCreationForm
from myapp.models import CarrierUser, CarrierEmployeeProfile

class CarrierEmployeeRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    position = forms.ChoiceField(choices=CarrierEmployeeProfile.POSITION_CHOICES)
    phone_number = forms.CharField(required=True)
    extension = forms.CharField(required=False)

    class Meta:
        model = CarrierUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Puedes usar el email como username
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            CarrierEmployeeProfile.objects.create(
                user=user,
                position=self.cleaned_data['position'],
                phone_number=self.cleaned_data['phone_number'],
                extension=self.cleaned_data['extension']
            )
        return user