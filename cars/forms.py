from django import forms
from .models import Car, ServiceHistory , MileageRecord

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
        
class MileageUpdateForm(forms.ModelForm):
    class Meta:
        model = MileageRecord
        fields = ['mileage', 'notes']
        widgets = {
            'notes': forms.TextInput(attrs={'placeholder': 'Optional notes about this mileage update'})
        }
    
    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop('car', None)
        super().__init__(*args, **kwargs)
        
        if self.car:
            self.fields['mileage'].widget.attrs.update({
                'min': self.car.current_mileage,
                'placeholder': f'Current: {self.car.current_mileage} km'
            })
            self.fields['mileage'].help_text = f'Must be greater than current mileage ({self.car.current_mileage} km)'
    
    def clean_mileage(self):
        mileage = self.cleaned_data.get('mileage')
        if self.car and mileage < self.car.current_mileage:
            raise forms.ValidationError(f"New mileage must be greater than current mileage ({self.car.current_mileage} km)")
        return mileage