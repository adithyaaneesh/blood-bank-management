from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, LoginForm
from .models import BloodStock
from django.contrib.auth import get_user_model
from django.db.models import Sum

User = get_user_model()


def user_register(request):
    if request.method == 'POST':
        form_data = UserRegistrationForm(request.POST)
        if form_data.is_valid():
            form_data.save()
            return redirect('login')
    else:
        form_data = UserRegistrationForm()
    return render(request,'register.html',{'form':form_data}) 

        
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

def user_logout(request):
    logout(request)
    return redirect('login')


def index(request):
    return render(request,'index.html')

def contact(request):
    return render(request,'contact.html')

def dashboard(request):
    total_units = BloodStock.objects.aggregate(total=Sum('units'))['total'] or 0
    blood_data = {group: 0 for group, _ in BloodStock.BLOOD_GROUPS}
    for stock in BloodStock.objects.all():
        blood_data[stock.blood_group] = stock.units

    context = {
        'available_donors': 24,
        'total_blood_units': total_units,
        'total_requests': 42, 
        'approved_requests': 38, 
        'a_positive': blood_data['A+'],
        'a_negative': blood_data['A-'],
        'b_positive': blood_data['B+'],
        'b_negative': blood_data['B-'],
        'ab_positive': blood_data['AB+'],
        'ab_negative': blood_data['AB-'],
        'o_positive': blood_data['O+'],
        'o_negative': blood_data['O-'],
        'blood_stock': total_units, 
    }
    return render(request, 'admin/admin_dashboard.html', context)


def stock_details(request):
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'patient/stock_details.html', {'stocks': stocks})

def blood_stock_list(request):
    stocks = BloodStock.objects.all()
    return render(request,'admin/blood_stock_list.html',{'stocks':stocks})

def add_blood_stock(request):
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units = request.POST.get('units')
        if blood_group and units:
            units = int(units)
            existing_stock = BloodStock.objects.filter(blood_group=blood_group).first()
            if existing_stock:
                existing_stock.units += units
                existing_stock.save()
            else:
                BloodStock.objects.create(blood_group=blood_group, units=units)
        return redirect('blood_stock_list')
    return render(request, 'admin/add_blood_stock.html')


def update_blood_stock(request, stock_id):
    stock = get_object_or_404(BloodStock, id=stock_id)
    if request.method == 'POST':
        stock.units = request.POST.get('units')
        stock.save()
        return redirect('blood_stock_list')
    return render(request,'admin/update_blood_stock.html',{'stock':stock})

def delete_blood_stock(request, stock_id):
    stock = get_object_or_404(BloodStock, id=stock_id)
    stock.delete()
    return redirect('blood_stock_list')

def patient_home(request):
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'patient/patient_home.html',{'stocks':stocks})

def donate_form(request):
    return render(request, 'patient/donate_form.html')

def request_form(request):
    return render(request, 'patient/request_form.html')

def hospital_home(request):
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'hospital/hospital_home.html',{'stocks':stocks})

def hospital_stock(request):
    stocks = BloodStock.objects.all()
    blood_data = {group: 0 for group, _ in BloodStock.BLOOD_GROUPS}
    for stock in stocks:
        blood_data[stock.blood_group] = stock.units
    context = {
        'a_positive': blood_data['A+'],
        'a_negative': blood_data['A-'],
        'b_positive': blood_data['B+'],
        'b_negative': blood_data['B-'],
        'ab_positive': blood_data['AB+'],
        'ab_negative': blood_data['AB-'],
        'o_positive': blood_data['O+'],
        'o_negative': blood_data['O-'],
    }
    return render(request, 'hospital/hospital_stocks.html', context)

