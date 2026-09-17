from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import EmailLoginForm, RegistrationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("generator:home")
    form = EmailLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("generator:home")
    return render(request, "accounts/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("generator:home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("generator:home")
    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect("accounts:login")