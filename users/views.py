from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
import logging
from .forms import CustomUserCreationForm

logger = logging.getLogger('shop')
def register_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('book_list'))

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"New user registered: {user.username}")
            return redirect(reverse('book_list'))
        else:
            logger.warning(f"Failed registration attempt with data: {request.POST}, errors: {form.errors}")
            return render(request, 'register.html', {'form': form, 'error': "Invalid input data"})
    else:
        form = UserCreationForm()
        return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('book_list'))
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, form.get_user())
                logger.info(f"User logged in: {username}")
                return redirect(reverse('book_list'))
        else:
            logger.warning(f"Failed login attempt with username: {request.POST.get('username')}, errors: {form.errors}")
            return render(request, 'login.html', {'form': form, 'error': "Invalid username or password"})
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    logger.info(f"User logged out: {request.user.username}")
    return redirect(reverse('book_list'))