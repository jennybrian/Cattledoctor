from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from .forms import CustomAuthenticationForm

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User won't be able to login until email is verified
            user.verification_token = get_random_string(64)
            user.save()

            # Send verification email
            verification_link = f"{request.scheme}://{request.get_host()}/verify-email/{user.verification_token}/"
            email_context = {
                'user': user,
                'verification_link': verification_link,
            }
            email_html = render_to_string('accounts/email/verification_email.html', email_context)
            
            send_mail(
                'Verify your email - Cattle Diagnosis',
                'Please verify your email to complete registration.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=email_html,
                fail_silently=False,
            )
            
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify_email(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token)
        user.is_active = True
        user.email_verified = True
        user.verification_token = ''
        user.save()
        messages.success(request, 'Email verified successfully! You can now login.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    return redirect('login')

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Login failed. Please check your credentials.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def home(request):
    return render(request, "accounts/home.html")

@login_required
def diagnosis_home(request):
    return render(request, "diagnosis/index.html")

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')