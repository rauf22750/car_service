from django.contrib import admin
from .models import Car, ServiceType, ServiceHistory, ServiceRecommendation ,MileageRecord

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'make', 'model', 'year', 'user', 'mileage', 'mot_expiry_date')
    list_filter = ('make', 'fuel_type')
    search_fields = ('registration_number', 'make', 'model', 'user__username')
    date_hierarchy = 'mot_expiry_date'

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price')
    search_fields = ('name', 'description')

@admin.register(ServiceHistory)
class ServiceHistoryAdmin(admin.ModelAdmin):
    list_display = ('car', 'service_type', 'service_date', 'mileage_at_service', 'price_paid')
    list_filter = ('service_type', 'service_date')
    search_fields = ('car__registration_number', 'service_type__name', 'notes')
    date_hierarchy = 'service_date'

@admin.register(ServiceRecommendation)
class ServiceRecommendationAdmin(admin.ModelAdmin):
    list_display = ('car', 'service_type', 'recommended_date', 'status', 'price')
    list_filter = ('service_type', 'status', 'recommended_date')
    search_fields = ('car__registration_number', 'service_type__name', 'reason')
    date_hierarchy = 'recommended_date'
    
# Add this to your existing admin.py file

@admin.register(MileageRecord)
class MileageRecordAdmin(admin.ModelAdmin):
    list_display = ('car', 'mileage', 'recorded_date', 'recorded_time', 'notes')
    list_filter = ('recorded_date',)
    search_fields = ('car__registration_number', 'notes')
    date_hierarchy = 'recorded_date'