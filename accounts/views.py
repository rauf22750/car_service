from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ProfileForm
from .models import Profile

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            # Create user profile
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            # Log the user in
            login(request, user)
            return redirect('dashboard')
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm()
    
    return render(request, 'accounts/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
        profile.save()
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {
        'profile_form': profile_form
    })
