from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
# flash messages
from django.contrib import messages
# decorators to change the restrict some pages
from django.contrib.auth.decorators import login_required

# Create your views here.
from .forms import CreateUserForm

def register_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()

        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')  # get the username only from the form
                messages.success(request, user + 'was successfully created!')
                return redirect('login')


    context = {'form': form}
    return render(request, 'accounts/register.html', context)

def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username or Password is incorrect!')

        context = {}
        return render(request, 'accounts/login.html', context)

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    return render(request, 'accounts/home.html')

def products(request):
    return render(request, 'accounts/products.html')

@login_required(login_url='login')
def users(request):
    return render(request, 'accounts/userList.html')
