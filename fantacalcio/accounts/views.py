from django.shortcuts import render, redirect
from .forms import LoginForm, RegistrationForm
from django.contrib.auth.models import User
from .models import Profile
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        form=LoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Username o password non validi")
                return render(request, "accounts/login.html", {"form":form})
        else:
            return render(request, "accounts/login.html", {"form":form})
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form":form})

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            password=form.cleaned_data['password']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            try:
                with transaction.atomic():
                    user=User.objects.create_user(username=username, email=email, password=password)
                    Profile.objects.create(user=user, telefono=form.cleaned_data['telefono'])
                return redirect('home')
            except IntegrityError:
                form.add_error(None, "Username o email già esistenti")
                return render(request, "accounts/register.html", {"form": form})
            except ValidationError as e:
                form.add_error(None, f"Errore di validazione: {e}")
                return render(request, "accounts/register.html", {"form": form})
        else:
            return render(request, "accounts/register.html", {"form": form})
    else:
        form=RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})
