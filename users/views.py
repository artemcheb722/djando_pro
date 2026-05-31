from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from .forms import CustomUserCreationForm
def register_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('book_list'))

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('book_list'))
        else:
            form = UserCreationForm()
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
                return redirect(reverse('book_list'))
        else:
            form = AuthenticationForm()
            return render(request, 'login.html', {'form': form, 'error': "Invalid username or password"})
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect(reverse('book_list'))