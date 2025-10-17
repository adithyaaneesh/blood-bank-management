from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm,HospitalRegistrationForm
from .models import BloodStock, DonorForm, RequestForm, HospitalRequestForm, Credential
from django.contrib.auth import get_user_model
from django.db.models import Sum

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']
            Credential.objects.create(user=user, role=role)
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def hospital_register(request):
    if request.method == "POST":
        form = HospitalRegistrationForm(request.POST)
        if form.is_valid():
            hospital_user = form.save()
            Credential.objects.create(user=hospital_user, role='Hospital')
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = HospitalRegistrationForm()
    return render(request, 'hospital_register.html', {'form': form})

def user_login(request):
    admin_user = User.objects.filter(is_superuser=True).first()
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('dashboard')
            role = getattr(user.credential, 'role', None)
            if role == 'Hospital':
                return redirect('hospitalhome')
            elif role == 'Patient':
                return redirect('patienthome')
            elif role == 'Donor':
                return redirect('donorhome')
            else:
                return redirect('home')
        return render(request, "login.html", {'error': 'Invalid username or password'})
    return render(request, "login.html", {'admin_user': admin_user})


def user_logout(request):
    logout(request)
    return redirect('login')

def index(request):
    return render(request,'index.html')

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
def donor_home(request):
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'donor/donor_home.html',{'stocks':stocks})

def donate_form(request):
    if request.method == 'POST':
        DonorForm.objects.create(
            firstname = request.POST.get('fname'),
            email = request.POST.get('email'),
            phone = request.POST.get('phonenum'),
            age = request.POST.get('age'),
            blood_group = request.POST.get('blood_group'),
            units = request.POST.get('units'),
            gender = request.POST.get('gender'),
            last_donate_date = request.POST.get('donatedate'),
            last_receive_date = request.POST.get('recieveddate'),
        )
        # messages.success(request,"Donation details submitted successfully!") 
        return redirect('donorhome')
    return render(request, 'donor/donate_form.html')

def request_form(request):
    if request.method == 'POST':
        RequestForm.objects.create(
            firstname = request.POST.get('fname'),
            email = request.POST.get('email'),
            phone = request.POST.get('phonenum'),
            age = request.POST.get('age'),
            reason = request.POST.get('reason'),
            blood_group = request.POST.get('blood_group'),
            units = request.POST.get('units'),
            gender = request.POST.get('gender'),
        )
        return redirect('patienthome')
    return render(request, 'patient/request_form.html')

def hospital_home(request):
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'hospital/hospital_home.html',{'stocks':stocks})

def hospital_request_form(request):
    if request.method == 'POST':
        HospitalRequestForm.objects.create(
            hospitalname = request.POST.get('hospitalname'),
            email = request.POST.get('email'),
            phone = request.POST.get('phonenum'),
            address = request.POST.get('address'),
            blood_group = request.POST.get('blood_group'),
            units = request.POST.get('units'),
        )
        return redirect('hospitalhome')
    return render(request,'hospital/hospital_request_form.html')

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

def admin_donors(request):
    donors = Credential.objects.filter(role='Donor').select_related('user')
    return render(request, 'admin/admin_donors.html', {'donors': donors})

def admin_patients(request):
    patients = Credential.objects.filter(role='Patient').select_related('user')
    return render(request, 'admin/admin_patients.html', {'patients': patients})

def admin_hospitals(request):
    hospitals = Credential.objects.filter(role='Hospital').select_related('user')
    return render(request, 'admin/admin_hospitals.html', {'hospitals': hospitals})
