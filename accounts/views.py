from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm
import random
from django.core.mail import send_mail
from django.conf import settings

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():

            User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            messages.success(request, "Account created successfully")
            return redirect('login_view')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form, 'page_title': 'Sign Up'})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print("EMAIL:", email)
        print("PASSWORD:", password)

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
            user = authenticate(request, username=username, password=password)
        except User.DoesNotExist:
            user = None

        print("USER:", user)  # DEBUG

        if user is not None:
            login(request, user)
            return redirect("home_page")
        else:
            messages.error(request, "User does not exist or wrong password.")

    return render(request, "accounts/login.html", {'page_title': 'Sign In'})

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            otp = str(random.randint(100000, 999999))

            # Save in session
            request.session['reset_email'] = email
            request.session['otp'] = otp

            # Send email
            send_mail(
                "Your OTP Code",
                f"Your OTP is {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return redirect('verify_otp')

        except User.DoesNotExist:
            messages.error(request, "Email not registered")

    return render(request, "accounts/forgot_password.html")


def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        session_otp = request.session.get("otp")

        if entered_otp == session_otp:
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid OTP")

    return render(request, "accounts/verify_otp.html")

def reset_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        email = request.session.get("reset_email")

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        messages.success(request, "Password reset successful")
        return redirect("accounts:login_view")

    return render(request, "accounts/reset_password.html")


def logout_view(request):
    logout(request)
    return redirect('login')