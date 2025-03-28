from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Car(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('lpg', 'LPG'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    registration_number = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    mileage = models.IntegerField()
    engine_size = models.DecimalField(max_digits=3, decimal_places=1)
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES)
    mot_expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.registration_number} - {self.make} {self.model}"
    
    def is_mot_due(self):
        return self.mot_expiry_date <= timezone.now().date() + datetime.timedelta(days=30)


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