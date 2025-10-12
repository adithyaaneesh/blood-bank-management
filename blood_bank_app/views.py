from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, LoginForm
from .models import BloodStock
from django.contrib.auth import get_user_model
User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm(request.POST)
    return render(request,'register.html', {'form':form})

def user_login(request):
    if request.method == 'POST':
        user_data = LoginForm(request, data=request.POST) 
        if user_data.is_valid():
            user = user_data.get_user() 
            login(request, user)
            return redirect('contact')
    else:
        user_data = LoginForm()
    return render(request, 'login.html', {'form':user_data})

def index(request):
    return render(request,'index.html')
def contact(request):
    return render(request,'contact.html')

def blood_stock_list(request):
    stocks = BloodStock.objects.all()
    return render(request,'blood_stock_list.html',{'stocks':stocks})

def add_blood_stock(request):
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units = request.POST.get('units')
        if blood_group and units:
            BloodStock.objects.create(blood_group=blood_group, units=units)
        return redirect('blood_stock_list')
    return render(request,'add_blood_stock.html')

def update_blood_stock(request, stock_id):
    stock = get_object_or_404(BloodStock, id=stock_id)
    if request.method == 'POST':
        stock.units = request.POST.get('units')
        stock.save()
        return redirect('blood_stock_list')
    return render(request,'update_blood_stock.html',{'stock':stock})

def delete_blood_stock(request, stock_id):
    stock = get_object_or_404(BloodStock, id=stock_id)
    stock.delete()
    return redirect('blood_stock_list')


