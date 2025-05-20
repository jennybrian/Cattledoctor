import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm

@login_required
def home(request):
    """Home view that requires authentication"""
    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})