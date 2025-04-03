# Add these functions to your existing views.py file
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Car, ServiceRecommendation, ServiceHistory, MileageRecord
from .forms import MileageUpdateForm, CarRegistrationForm , ServiceHistoryForm
from .services import check_service_recommendations

# Update the schedule_service view in views.py
@login_required
def service_recommendations(request, car_id):
    """
    View to display and refresh service recommendations for a specific car.
    """
    car = get_object_or_404(Car, id=car_id, user=request.user)
    
    # Check if we need to refresh recommendations
    if request.GET.get('refresh') == '1':
        # Clear existing pending recommendations
        ServiceRecommendation.objects.filter(car=car, status='pending').delete()
        
        # Generate new recommendations
        check_service_recommendations(car)
        messages.success(request, "Service recommendations refreshed.")
    
    # Get all recommendations for this car
    recommendations = ServiceRecommendation.objects.filter(car=car).order_by('status', '-recommended_date')
    
    return render(request, 'cars/service_recommendations.html', {
        'car': car,
        'recommendations': recommendations
    })
@login_required
def dashboard(request):
    cars = Car.objects.filter(user=request.user)
    recommendations = ServiceRecommendation.objects.filter(
        car__user=request.user, 
        status='pending'
    ).order_by('recommended_date')
    
    return render(request, 'cars/dashboard.html', {
        'cars': cars,
        'recommendations': recommendations
    })

@login_required
def car_list(request):
    cars = Car.objects.filter(user=request.user)
    return render(request, 'cars/car_list.html', {'cars': cars})



@login_required
def service_history(request, car_id):
    car = get_object_or_404(Car, id=car_id, user=request.user)
    history = car.service_history.all().order_by('-service_date')
    
    if request.method == 'POST':
        form = ServiceHistoryForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.car = car
            service.save()
            
            # Update car mileage if the service mileage is higher
            if service.mileage_at_service > car.mileage:
                car.mileage = service.mileage_at_service
                car.save()
            
            # Check for new service recommendations
            check_service_recommendations(car)
            
            messages.success(request, "Service record added successfully!")
            return redirect('service_history', car_id=car.id)
    else:
        form = ServiceHistoryForm(initial={'mileage_at_service': car.mileage})
    
    return render(request, 'cars/service_history.html', {
        'car': car,
        'history': history,
        'form': form
    })



@login_required
def schedule_service(request):
    if request.method == 'POST':
        recommendation_ids = request.POST.getlist('recommendation_ids')
        
        if not recommendation_ids:
            messages.error(request, "No services selected.")
            return redirect('dashboard')
        
        # Store the selected recommendation IDs in the session
        request.session['selected_recommendation_ids'] = recommendation_ids
        
        # Redirect to the checkout page
        return redirect('service_checkout')
    
    return redirect('dashboard')

@login_required
def service_checkout(request):
    # Get the selected recommendation IDs from the session
    recommendation_ids = request.session.get('selected_recommendation_ids', [])
    
    if not recommendation_ids:
        messages.error(request, "No services selected.")
        return redirect('dashboard')
    
    # Get the recommendations
    recommendations = ServiceRecommendation.objects.filter(
        id__in=recommendation_ids,
        car__user=request.user,
        status='pending'
    )
    
    if not recommendations:
        messages.error(request, "No valid services selected.")
        return redirect('dashboard')
    
    # Calculate prices
    subtotal = sum(rec.price for rec in recommendations)
    vat = subtotal * 0.2  # 20% VAT
    total_price = subtotal + vat
    
    # Get unique vehicles
    vehicles = set(rec.car for rec in recommendations)
    
    return render(request, 'cars/service_checkout.html', {
        'recommendations': recommendations,
        'vehicles': vehicles,
        'subtotal': subtotal,
        'vat': vat,
        'total_price': total_price,
    })

@login_required
def confirm_checkout(request):
    if request.method == 'POST':
        # Get the selected recommendation IDs from the session
        recommendation_ids = request.session.get('selected_recommendation_ids', [])
        service_date = request.POST.get('service_date')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes')
        
        if not recommendation_ids or not service_date or not payment_method:
            messages.error(request, "Invalid checkout data.")
            return redirect('dashboard')
        
        # Get the recommendations
        recommendations = ServiceRecommendation.objects.filter(
            id__in=recommendation_ids,
            car__user=request.user,
            status='pending'
        )
        
        if not recommendations:
            messages.error(request, "No valid services selected.")
            return redirect('dashboard')
        
        # Update recommendations to scheduled status
        for recommendation in recommendations:
            recommendation.status = 'scheduled'
            recommendation.save()
        
        # Generate a summary
        vehicles = set(rec.car for rec in recommendations)
        subtotal = sum(rec.price for rec in recommendations)
        vat = subtotal * 0.2
        total_price = subtotal + vat
        
        # Clear the session data
        if 'selected_recommendation_ids' in request.session:
            del request.session['selected_recommendation_ids']
        
        # Render the confirmation page with the summary
        return render(request, 'cars/service_confirmation.html', {
            'recommendations': recommendations,
            'vehicles': vehicles,
            'service_date': service_date,
            'payment_method': payment_method,
            'notes': notes,
            'subtotal': subtotal,
            'vat': vat,
            'total_price': total_price,
        })
    
    return redirect('dashboard')

# Modify the car_detail view in your views.py file

@login_required
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id, user=request.user)
    
    if request.method == 'POST':
        mileage_form = MileageUpdateForm(request.POST, car=car)
        if mileage_form.is_valid():
            mileage_record = mileage_form.save(commit=False)
            mileage_record.car = car
            mileage_record.save()
            
            # Update the car's mileage field for backward compatibility
            car.mileage = mileage_record.mileage
            car.save()
            
            # Check for new service recommendations based on the updated mileage
            check_service_recommendations(car)
            
            messages.success(request, f"Mileage updated to {mileage_record.mileage} km")
            return redirect('car_detail', car_id=car.id)
    else:
        mileage_form = MileageUpdateForm(car=car, initial={'mileage': car.current_mileage})
    
    # Get pending service recommendations
    recommendations = ServiceRecommendation.objects.filter(car=car, status='pending')
    
    # Get recent service history
    service_history = ServiceHistory.objects.filter(car=car).order_by('-service_date')
    
    # Get mileage history
    mileage_history = car.mileage_records.all()[:10]  # Get the 10 most recent records
    
    return render(request, 'cars/car_detail.html', {
        'car': car,
        'mileage_form': mileage_form,
        'recommendations': recommendations,
        'service_history': service_history,
        'mileage_history': mileage_history,
    })

# Modify the car_register view in views.py

@login_required
def car_register(request):
    if request.method == 'POST':
        form = CarRegistrationForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            
            # Create initial mileage record
            MileageRecord.objects.create(
                car=car,
                mileage=car.mileage,
                notes="Initial registration"
            )
            
            # Check for service recommendations
            check_service_recommendations(car)
            
            messages.success(request, f"Vehicle {car.registration_number} registered successfully!")
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarRegistrationForm()
    
    return render(request, 'cars/car_register.html', {'form': form})

@login_required
def confirm_checkout(request):
    if request.method == 'POST':
        # Get the selected recommendation IDs from the session
        recommendation_ids = request.session.get('selected_recommendation_ids', [])
        service_date = request.POST.get('service_date')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes')
        
        if not recommendation_ids or not service_date or not payment_method:
            messages.error(request, "Invalid checkout data.")
            return redirect('dashboard')
        
        # Get the recommendations
        recommendations = ServiceRecommendation.objects.filter(
            id__in=recommendation_ids,
            car__user=request.user,
            status='pending'
        )
        
        if not recommendations:
            messages.error(request, "No valid services selected.")
            return redirect('dashboard')
        
        # Update recommendations to scheduled status
        for recommendation in recommendations:
            recommendation.status = 'scheduled'
            recommendation.save()
        
        # Generate a summary
        vehicles = list(set(rec.car for rec in recommendations))
        subtotal = sum(rec.price for rec in recommendations)
        vat = subtotal * 0.2
        total_price = subtotal + vat
        
        # Store confirmation data in the session
        request.session['confirmation_data'] = {
            'recommendations': [
                {
                    'car_registration': rec.car.registration_number,
                    'car_make': rec.car.make,
                    'car_model': rec.car.model,
                    'service_type': rec.service_type.name,
                    'price': float(rec.price)
                }
                for rec in recommendations
            ],
            'vehicles': [
                {
                    'registration': car.registration_number,
                    'make': car.make,
                    'model': car.model
                }
                for car in vehicles
            ],
            'service_date': service_date,
            'payment_method': payment_method,
            'notes': notes,
            'subtotal': float(subtotal),
            'vat': float(vat),
            'total_price': float(total_price)
        }
        
        # Clear the recommendation IDs from the session
        if 'selected_recommendation_ids' in request.session:
            del request.session['selected_recommendation_ids']
        
        # Redirect to the confirmation page
        return redirect('service_confirmation')
    
    return redirect('dashboard')