from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Car, ServiceType, ServiceHistory, ServiceRecommendation
from .forms import CarRegistrationForm, UpdateMileageForm, ServiceHistoryForm
from .services import check_service_recommendations

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
def car_register(request):
    if request.method == 'POST':
        form = CarRegistrationForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            
            # Generate initial service recommendations
            check_service_recommendations(car)
            
            messages.success(request, f"Vehicle {car.registration_number} registered successfully!")
            return redirect('dashboard')
    else:
        form = CarRegistrationForm()
    
    return render(request, 'cars/car_register.html', {
        'form': form,
        'cars': Car.objects.filter(user=request.user)
    })

@login_required
def car_list(request):
    cars = Car.objects.filter(user=request.user)
    return render(request, 'cars/car_list.html', {'cars': cars})

@login_required
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id, user=request.user)
    service_history = car.service_history.all().order_by('-service_date')
    recommendations = car.service_recommendations.filter(status='pending')
    
    # Update mileage form
    if request.method == 'POST':
        mileage_form = UpdateMileageForm(request.POST, instance=car)
        if mileage_form.is_valid():
            mileage_form.save()
            # Check for new service recommendations based on updated mileage
            check_service_recommendations(car)
            messages.success(request, "Mileage updated successfully!")
            return redirect('car_detail', car_id=car.id)
    else:
        mileage_form = UpdateMileageForm(instance=car)
    
    return render(request, 'cars/car_detail.html', {
        'car': car,
        'service_history': service_history,
        'recommendations': recommendations,
        'mileage_form': mileage_form
    })

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
def service_recommendations(request, car_id):
    car = get_object_or_404(Car, id=car_id, user=request.user)
    
    # Force check for new recommendations
    if 'refresh' in request.GET:
        check_service_recommendations(car)
        messages.success(request, "Service recommendations updated!")
    
    recommendations = car.service_recommendations.all().order_by('status', 'recommended_date')
    
    return render(request, 'cars/service_recommendations.html', {
        'car': car,
        'recommendations': recommendations
    })

@login_required
def schedule_service(request):
    if request.method == 'POST':
        recommendation_ids = request.POST.getlist('recommendation_ids')
        recommendations = ServiceRecommendation.objects.filter(
            id__in=recommendation_ids,
            car__user=request.user,
            status='pending'
        )
        
        if not recommendations:
            messages.error(request, "No valid services selected.")
            return redirect('dashboard')
        
        # Calculate total price
        total_price = recommendations.aggregate(Sum('price'))['price__sum'] or 0
        
        # Update status to scheduled
        for recommendation in recommendations:
            recommendation.status = 'scheduled'
            recommendation.save()
        
        messages.success(request, f"Services scheduled successfully! Total price: £{total_price:.2f}")
        return redirect('dashboard')
    
    # If not POST, redirect to dashboard
    return redirect('dashboard')

@login_required
def service_checkout(request):
    if request.method == 'POST':
        recommendation_ids = request.POST.getlist('recommendation_ids')
        recommendations = ServiceRecommendation.objects.filter(
            id__in=recommendation_ids,
            car__user=request.user,
            status='pending'
        )
        
        if not recommendations:
            messages.error(request, "No valid services selected.")
            return redirect('dashboard')
        
        # Calculate prices
        subtotal = recommendations.aggregate(Sum('price'))['price__sum'] or 0
        vat = subtotal * 0.2  # 20% VAT
        total_price = subtotal + vat
        
        # Get unique vehicles
        vehicles = set([rec.car for rec in recommendations])
        
        return render(request, 'cars/service_checkout.html', {
            'recommendations': recommendations,
            'vehicles': vehicles,
            'subtotal': subtotal,
            'vat': vat,
            'total_price': total_price,
        })
    
    # If not POST, redirect to dashboard
    return redirect('dashboard')

@login_required
def confirm_checkout(request):
    if request.method == 'POST':
        recommendation_ids = request.POST.getlist('recommendation_ids')
        service_date = request.POST.get('service_date')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes')
        
        recommendations = ServiceRecommendation.objects.filter(
            id__in=recommendation_ids,
            car__user=request.user
        )
        
        if not recommendations or not service_date or not payment_method:
            messages.error(request, "Invalid checkout data.")
            return redirect('dashboard')
        
        # Update recommendations to scheduled status
        for recommendation in recommendations:
            recommendation.status = 'scheduled'
            recommendation.save()
        
        messages.success(request, "Services scheduled successfully! We will contact you to confirm your appointment.")
        return redirect('dashboard')
    
    # If not POST, redirect to dashboard
    return redirect('dashboard')