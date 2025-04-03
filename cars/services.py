from django.utils import timezone
import datetime
from .models import Car, ServiceType, ServiceHistory, ServiceRecommendation

def check_service_recommendations(car):
    """
    Check and create service recommendations for a car based on:
    - Mileage history
    - Time since last service
    - MOT expiry
    """
    recommendations = []
    
    # Get the latest service history for each service type
    latest_services = {}
    for history in car.service_history.all():
        service_type = history.service_type
        if service_type.id not in latest_services or history.service_date > latest_services[service_type.id]['date']:
            latest_services[service_type.id] = {
                'date': history.service_date,
                'mileage': history.mileage_at_service,
                'service': history
            }
    
    # Get the current mileage from the latest mileage record
    current_mileage = car.current_mileage
    
    # Check for oil change (every 3,000 km or 6 months)
    try:
        oil_change_type = ServiceType.objects.get(name='Oil Change')
        if oil_change_type.id in latest_services:
            last_oil_change = latest_services[oil_change_type.id]
            mileage_diff = current_mileage - last_oil_change['mileage']
            date_diff = (timezone.now().date() - last_oil_change['date']).days
            
            if mileage_diff >= 3000 or date_diff >= 180:  # 6 months in days
                reason = []
                if mileage_diff >= 3000:
                    reason.append(f"Mileage increased by {mileage_diff} km since last oil change")
                if date_diff >= 180:
                    reason.append(f"Last oil change was {date_diff} days ago")
                
                # Calculate price (10% increase if not serviced in the last year)
                price = oil_change_type.base_price
                if date_diff > 365:  # More than a year
                    price *= 1.1
                
                # Create recommendation
                recommendation = ServiceRecommendation(
                    car=car,
                    service_type=oil_change_type,
                    recommended_date=timezone.now().date(),
                    recommended_mileage=current_mileage,
                    reason=", ".join(reason),
                    price=price
                )
                recommendations.append(recommendation)
        else:
            # No oil change history, recommend one
            recommendation = ServiceRecommendation(
                car=car,
                service_type=oil_change_type,
                recommended_date=timezone.now().date(),
                recommended_mileage=current_mileage,
                reason="Initial oil change recommended",
                price=oil_change_type.base_price
            )
            recommendations.append(recommendation)
    except ServiceType.DoesNotExist:
        # Oil change service type doesn't exist, skip this recommendation
        pass
    
    # Check for tyre replacement (every 20,000 km)
    try:
        tyre_type = ServiceType.objects.get(name='Tyre Replacement')
        if tyre_type.id in latest_services:
            last_tyre_change = latest_services[tyre_type.id]
            mileage_diff = current_mileage - last_tyre_change['mileage']
            date_diff = (timezone.now().date() - last_tyre_change['date']).days
            
            if mileage_diff >= 20000:
                # Calculate price (10% increase if not serviced in the last year)
                price = tyre_type.base_price
                if date_diff > 365:  # More than a year
                    price *= 1.1
                
                # Create recommendation
                recommendation = ServiceRecommendation(
                    car=car,
                    service_type=tyre_type,
                    recommended_date=timezone.now().date(),
                    recommended_mileage=current_mileage,
                    reason=f"Mileage increased by {mileage_diff} km since last tyre replacement",
                    price=price
                )
                recommendations.append(recommendation)
        else:
            # No tyre replacement history, recommend one if the car has high mileage
            if current_mileage > 20000:
                recommendation = ServiceRecommendation(
                    car=car,
                    service_type=tyre_type,
                    recommended_date=timezone.now().date(),
                    recommended_mileage=current_mileage,
                    reason="Initial tyre replacement recommended due to high mileage",
                    price=tyre_type.base_price
                )
                recommendations.append(recommendation)
    except ServiceType.DoesNotExist:
        # Tyre replacement service type doesn't exist, skip this recommendation
        pass
    
    # Continue with other service checks using current_mileage instead of car.mileage
    # ...
    
    # Save all recommendations
    for recommendation in recommendations:
        # Check if a similar recommendation already exists
        existing = ServiceRecommendation.objects.filter(
            car=car,
            service_type=recommendation.service_type,
            status='pending'
        ).first()
        
        if not existing:
            recommendation.save()
    
    return recommendations