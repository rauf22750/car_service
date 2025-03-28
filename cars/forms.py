from django import forms
from .models import Car, ServiceHistory

class CarRegistrationForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['registration_number', 'make', 'model', 'year', 'mileage', 
                  'engine_size', 'fuel_type', 'mot_expiry_date']
        widgets = {
            'mot_expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class UpdateMileageForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['mileage']

class ServiceHistoryForm(forms.ModelForm):
    class Meta:
        model = ServiceHistory
        fields = ['service_type', 'service_date', 'mileage_at_service', 'price_paid', 'notes']
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date'}),
        }