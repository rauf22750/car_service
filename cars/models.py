from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Car(models.Model):
    # Keep existing fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    registration_number = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    engine_size = models.DecimalField(max_digits=3, decimal_places=1)
    FUEL_CHOICES = (
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('plugin_hybrid', 'Plug-in Hybrid'),
    )
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    mileage = models.PositiveIntegerField()  # Keep this for backward compatibility
    mot_expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.registration_number} - {self.make} {self.model}"
    
    @property
    def current_mileage(self):
        """Get the current mileage from the latest mileage record"""
        latest_record = self.mileage_records.first()
        if latest_record:
            return latest_record.mileage
        return self.mileage  # Fallback to the original mileage field
    
    @property
    def mileage_history(self):
        """Get the mileage history in chronological order"""
        return self.mileage_records.all().order_by('recorded_date', 'recorded_time')
    
    @property
    def is_mot_due(self):
        """Check if MOT is due within 30 days"""
        today = timezone.now().date()
        days_to_mot = (self.mot_expiry_date - today).days
        return days_to_mot <= 30
class ServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return self.name


class ServiceHistory(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='service_history')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    service_date = models.DateField()
    mileage_at_service = models.IntegerField()
    price_paid = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.car.registration_number} - {self.service_type.name} on {self.service_date}"
    
    class Meta:
        ordering = ['-service_date']


class ServiceRecommendation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
    ]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='service_recommendations')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    recommended_date = models.DateField()
    recommended_mileage = models.IntegerField(blank=True, null=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.car.registration_number} - {self.service_type.name} ({self.status})"
    
    # Add this to your existing models.py file

class MileageRecord(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='mileage_records')
    mileage = models.PositiveIntegerField()
    recorded_date = models.DateField(auto_now_add=True)
    recorded_time = models.TimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-recorded_date', '-recorded_time']

    def __str__(self):
        return f"{self.car.registration_number} - {self.mileage}km on {self.recorded_date}"