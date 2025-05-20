import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

@login_required
def home(request):
    """Home page view requiring authentication"""
    return render(request, "home.html")

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        try:
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = True  # Set to True until email verification is implemented
                user.save()
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify_email(request, token):
    # Email verification logic will be implemented later
    return redirect('login')