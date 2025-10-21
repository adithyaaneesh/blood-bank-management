from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm
from .models import (
    BloodRequest, BloodStock, DonorForm, Credential
)

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Credential.objects.create(user=user, role=form.cleaned_data['role'])
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    admin_user = User.objects.filter(is_superuser=True).first()
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_superuser and selected_role == 'Admin':
                login(request, user)
                return redirect('dashboard')
            role = getattr(user.credential, 'role', None)
            if role == selected_role:
                login(request, user)
                redirect_map = {
                    'Hospital': 'hospitalhome',
                    'Patient': 'patienthome',
                    'Donor': 'donateform'
                }
                return redirect(redirect_map.get(role, 'home'))
            else:
                return render(request, "login.html", {
                    'error': "Selected role doesn't match your account.",
                    'admin_user': admin_user
                })
        return render(request, "login.html", {
            'error': 'Invalid username or password',
            'admin_user': admin_user
        })
    return render(request, "login.html", {'admin_user': admin_user})


def user_logout(request):
    logout(request)
    return redirect('login')


def index(request):
    return render(request, 'index.html')


# Admin Dashboard Views

def dashboard(request):
    total_units = BloodStock.objects.aggregate(total=Sum('units'))['total'] or 0
    total_donors = DonorForm.objects.count()
    total_requests = DonorForm.objects.count() + BloodRequest.objects.count()
    donor_approved = DonorForm.objects.filter(status__iexact='Approved').count()
    blood_approved = BloodRequest.objects.filter(status__iexact='Accepted').exclude(role='Donor').count()
    approved_requests = donor_approved + blood_approved

    blood_data = {group: 0 for group, _ in BloodStock.BLOOD_GROUPS}
    for stock in BloodStock.objects.all():
        blood_data[stock.blood_group] = stock.units

    context = {
        'available_donors': total_donors,
        'total_blood_units': total_units,
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'a_positive': blood_data.get('A+', 0),
        'a_negative': blood_data.get('A-', 0),
        'b_positive': blood_data.get('B+', 0),
        'b_negative': blood_data.get('B-', 0),
        'ab_positive': blood_data.get('AB+', 0),
        'ab_negative': blood_data.get('AB-', 0),
        'o_positive': blood_data.get('O+', 0),
        'o_negative': blood_data.get('O-', 0),
        'blood_stock': total_units,
    }
    return render(request, 'admin/admin_dashboard.html', context)



# Blood Stock Views

def blood_stock_list(request):
    stocks = BloodStock.objects.all()
    expired_stocks = [s for s in stocks if s.is_expired()]
    near_expiry_stocks = [s for s in stocks if s.is_near_expiry()]

    context = {
        'stocks': stocks,
        'expired_stocks': expired_stocks,
        'near_expiry_stocks': near_expiry_stocks,
        'today': date.today(),
    }
    return render(request, 'admin/blood_stock_list.html', context)



def add_blood_stock(request):
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        units = int(request.POST.get('units', 0))
        if blood_group:
            stock, created = BloodStock.objects.get_or_create(blood_group=blood_group)
            stock.units += units
            stock.save()
        return redirect('blood_stock_list')
    return render(request, 'admin/add_blood_stock.html')


def update_blood_stock(request, stock_id):
    stock = get_object_or_404(BloodStock, id=stock_id)
    if request.method == 'POST':
        stock.units = int(request.POST.get('units', stock.units))
        stock.save()
        return redirect('blood_stock_list')
    return render(request, 'admin/update_blood_stock.html', {'stock': stock})


def delete_blood_stock(request, stock_id):
    stock = get_object_or_404(BloodStock, id=stock_id)
    stock.delete()
    return redirect('blood_stock_list')


def stock_details(request):
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'patient/stock_details.html', {'stocks': stocks})

#Donor views

def donate_form(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        DonorForm.objects.create(
            user=request.user,
            firstname=request.POST.get('fname'),
            # email=request.user.get('email'),
            email=request.user.email,
            phone=request.POST.get('phonenum'),
            age=request.POST.get('age'),
            blood_group=request.POST.get('blood_group'),
            units=request.POST.get('units'),
            gender=request.POST.get('gender'),
            last_donate_date=request.POST.get('donatedate') or None,
            last_receive_date=request.POST.get('recieveddate') or None,
            consent=request.POST.get('consent') == 'on',
            status='Pending'
        )
        return redirect('donor_history')

    return render(request, 'donor/donate_form.html')



def donor_home(request):
    donor_records = DonorForm.objects.filter(user=request.user)
    context = {
        'total_requests': donor_records.count(),
        'pending_requests': donor_records.filter(status='Pending').count(),
        'approved_requests': donor_records.filter(status='Approved').count(),
        'rejected_requests': donor_records.filter(status='Rejected').count(),
        'stocks': BloodStock.objects.all().order_by('blood_group'),
    }
    return render(request, 'donor/donor_home.html', context)


def admin_donors(request):
    donors = DonorForm.objects.all().order_by('-id')
    return render(request, 'admin/admin_donors.html', {'donors': donors})


def delete_all_donor_requests(request):
    if request.user.is_superuser:  
        DonorForm.objects.all().delete()
    return redirect('admin_donors')  

def update_donor_status(request, donor_id, status):
    donor = get_object_or_404(DonorForm, id=donor_id)
    donor.status = status
    donor.approved_by = request.user
    donor.save()

    if status == 'Approved':
        stock, _ = BloodStock.objects.get_or_create(blood_group=donor.blood_group)
        stock.units += donor.units
        stock.save()

    return redirect('admin_donors')



def donor_history(request):
    if not request.user.is_authenticated:
        return redirect('login')

    donor_records = DonorForm.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'donor/donor_history.html', {'donor_records': donor_records})


def delete_my_donor_requests(request):
    if request.user.is_authenticated:
        DonorForm.objects.filter(email=request.user.email).delete()
    return redirect('donor_history')



# Patient Views

def patient_home(request):
    patient_requests = BloodRequest.objects.filter(user=request.user)

    context = {
        'stocks': BloodStock.objects.all().order_by('blood_group'),
        'total_requests': patient_requests.count(),
        'pending_requests': patient_requests.filter(status='Pending').count(),
        'approved_requests': patient_requests.filter(status='Accepted').count(),
        'rejected_requests': patient_requests.filter(status='Rejected').count(),
        'username': request.user.username,
    }
    return render(request, 'patient/patient_home.html', context)

def request_form(request):
    if request.method == 'POST':
        BloodRequest.objects.create(
            user=request.user if request.user.is_authenticated else None,
            fname=request.POST.get('fname'),
            email=request.POST.get('email'),
            phonenum=request.POST.get('phonenum'),
            age=request.POST.get('age'),
            reason=request.POST.get('reason'),
            blood_group=request.POST.get('blood_group'),
            units=request.POST.get('units'),
            gender=request.POST.get('gender'),
            role='Patient',
            status='Pending'
        )
        return redirect('patienthome')
    return render(request, 'patient/request_form.html')


def patient_request_history(request):
    requests = BloodRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'patient/request_history.html', {'requests': requests})

# Admin Blood Request Actions

def admin_blood_request(request):
    requests_list = BloodRequest.objects.filter(role__in=['Patient', 'Hospital']).order_by('-created_at')
    return render(request, 'admin/admin_blood_request.html', {'requests': requests_list})


def approve_request(request, pk):
    req = get_object_or_404(BloodRequest, pk=pk)
    stock, _ = BloodStock.objects.get_or_create(blood_group=req.blood_group)
    units = int(req.units)

    if req.role == 'Donor':
        stock.units += units
        req.status = 'Accepted'
        donor = DonorForm.objects.filter(email=req.email, units=req.units, blood_group=req.blood_group).first()
        if donor:
            donor.status = 'Approved'
            donor.save()
    else:
        if stock.units >= units:
            stock.units -= units
            req.status = 'Accepted'
        else:
            req.status = 'Rejected'

    stock.save()
    req.save()
    return redirect('admin_blood_request')


def reject_request(request, pk):
    req = get_object_or_404(BloodRequest, pk=pk)
    req.status = 'Rejected'
    req.save()

    if req.role == 'Donor':
        donor = DonorForm.objects.filter(email=req.email, units=req.units, blood_group=req.blood_group).first()
        if donor:
            donor.status = 'Rejected'
            donor.save()
    return redirect('admin_blood_request')

# Hospital Views

def hospital_home(request):
    hospital_requests = BloodRequest.objects.filter(user=request.user, role='Hospital')
    context = {
        'stocks': BloodStock.objects.all().order_by('blood_group'),
        'total_requests': hospital_requests.count(),
        'approved_requests': hospital_requests.filter(status='Accepted').count(),
        'available_donors': DonorForm.objects.count(),
        'username': request.user.username,
    }
    return render(request, 'hospital/hospital_home.html', context)

def hospital_request_form(request):
    if request.method == 'POST':
        BloodRequest.objects.create(
            user=request.user,
            fname=request.POST.get('hospitalname'),
            email=request.POST.get('email'),
            phonenum=request.POST.get('phonenum'),
            age=0,
            reason=request.POST.get('address'),
            blood_group=request.POST.get('blood_group'),
            units=request.POST.get('units'),
            gender='N/A', 
            role='Hospital',
            status='Pending',
        )
        return redirect('hospital_request_history')
    return render(request, 'hospital/hospital_request_form.html')

def hospital_request_history(request):
    requests = BloodRequest.objects.filter(user=request.user, role='Hospital')
    return render(request, 'hospital/hospital_request_history.html', {'requests': requests})


def hospital_stock(request):
    stocks = BloodStock.objects.all()
    blood_data = {group: 0 for group, _ in BloodStock.BLOOD_GROUPS}
    for stock in stocks:
        blood_data[stock.blood_group] = stock.units
    context = {bg.lower().replace('+', '_positive').replace('-', '_negative'): units for bg, units in blood_data.items()}
    return render(request, 'hospital/hospital_stocks.html', context)

# Admin User Management

def admin_donors(request):
    donors = DonorForm.objects.all().order_by('-id')
    return render(request, 'admin/admin_donors.html', {'donors': donors})


def update_donor_status(request, donor_id, status):
    donor = get_object_or_404(DonorForm, id=donor_id)
    donor.status = status
    donor.approved_by = request.user
    donor.save()
    if status == 'Approved':
        stock, _ = BloodStock.objects.get_or_create(blood_group=donor.blood_group)
        stock.units += donor.units
        stock.save()
    return redirect('admin_donor_dashboard')


def admin_donor_list(request):
    donor_data = DonorForm.objects.all().order_by('-id')
    donors = Credential.objects.filter(role='Donor').select_related('user')
    return render(request, 'admin/admin_donors_list.html', {'donordata': donor_data, 'donors': donors})


def admin_patients(request):
    patients = Credential.objects.filter(role='Patient').select_related('user')
    return render(request, 'admin/admin_patients.html', {'patients': patients})


def admin_hospitals(request):
    hospitals = Credential.objects.filter(role='Hospital').select_related('user')
    return render(request, 'admin/admin_hospitals.html', {'hospitals': hospitals})

