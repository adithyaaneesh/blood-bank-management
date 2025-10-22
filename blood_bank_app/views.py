from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, HospitalForm, PatientProfileForm, DonorProfileForm
from .models import (
    BloodRequest, BloodStock, DonorForm, Credential, HospitalDetails, PatientProfile, DonorProfile
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
                if role == 'Hospital':
                    hospital_profile_exists = HospitalDetails.objects.filter(user=user).exists()
                    if not hospital_profile_exists:
                        return redirect('hospital_profile')
                    else:
                        return redirect('hospitalhome')
                elif role == 'Patient':
                    from .models import PatientProfile
                    patient_profile_exists = PatientProfile.objects.filter(user=user).exists()
                    if not patient_profile_exists:
                        return redirect('patient_profile')
                    else:
                        return redirect('patienthome')
                elif role == 'Donor':
                    from .models import DonorProfile
                    donor_profile_exists = DonorProfile.objects.filter(user=user).exists()
                    if not donor_profile_exists:
                        return redirect('donor_profile') 
                    else:
                        return redirect('donorhome') 
                return redirect('home')
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

# def dashboard(request):
#     total_units = BloodStock.objects.aggregate(total=Sum('units'))['total'] or 0
#     total_donors = DonorForm.objects.count()
#     total_requests = DonorForm.objects.count() + BloodRequest.objects.count()
#     donor_approved = DonorForm.objects.filter(status__iexact='Approved').count()
#     blood_approved = BloodRequest.objects.filter(status__iexact='Accepted').exclude(role='Donor').count()
#     approved_requests = donor_approved + blood_approved

@login_required
def dashboard(request):
    total_units = BloodStock.objects.aggregate(total=Sum('units'))['total'] or 0
    total_donors = DonorForm.objects.count()
    total_blood_requests = BloodRequest.objects.filter(role__in=['Patient', 'Hospital']).count() + BloodRequest.objects.count()
    donor_approved = DonorForm.objects.filter(status='Approved').count()
    blood_approved = BloodRequest.objects.filter(status='Accepted', role__in=['Patient', 'Hospital']).count()
    approved_requests = donor_approved + blood_approved

    blood_data = {group: 0 for group, _ in BloodStock.BLOOD_GROUPS}
    for stock in BloodStock.objects.all():
        blood_data[stock.blood_group] = stock.units

    context = {
        'available_donors': total_donors,
        'total_blood_units': total_units,
        'total_requests': total_blood_requests,
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

@login_required
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


@login_required
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

@login_required
def update_blood_stock(request, stock_id):
    stock = get_object_or_404(BloodStock, id=stock_id)
    if request.method == 'POST':
        stock.units = int(request.POST.get('units', stock.units))
        stock.save()
        return redirect('blood_stock_list')
    return render(request, 'admin/update_blood_stock.html', {'stock': stock})

@login_required
def delete_blood_stock(request, stock_id):
    stock = get_object_or_404(BloodStock, id=stock_id)
    stock.delete()
    return redirect('blood_stock_list')

@login_required
def stock_details(request):
    stocks = BloodStock.objects.all().order_by('blood_group')
    return render(request, 'patient/stock_details.html', {'stocks': stocks})

#Donor views

@login_required
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


@login_required
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

@login_required
def admin_donors(request):
    donors = DonorForm.objects.all().order_by('-id')
    return render(request, 'admin/admin_donors.html', {'donors': donors})

@login_required
def delete_all_donor_requests(request):
    if request.user.is_superuser:  
        DonorForm.objects.all().delete()
    return redirect('admin_donors')  

@login_required
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


@login_required
def donor_history(request):
    if not request.user.is_authenticated:
        return redirect('login')

    donor_records = DonorForm.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'donor/donor_history.html', {'donor_records': donor_records})

@login_required
def delete_my_donor_requests(request):
    if request.user.is_authenticated:
        DonorForm.objects.filter(email=request.user.email).delete()
    return redirect('donor_history')



# Patient Views

@login_required
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

@login_required
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

@login_required
def patient_request_history(request):
    requests = BloodRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'patient/request_history.html', {'requests': requests})

# Admin Blood Request Actions

@login_required
def admin_blood_request(request):
    requests_list = BloodRequest.objects.filter(role__in=['Patient', 'Hospital']).order_by('-created_at')
    return render(request, 'admin/admin_blood_request.html', {'requests': requests_list})


@login_required
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
        messages.success(request, f"Donor request approved and {units} units added to stock.")
    else:
        if stock.units >= units:
            stock.units -= units
            req.status = 'Accepted'
            req.admin_message = f"{units} units of {req.blood_group} provided successfully."
            messages.success(request, f"Blood request approved. {units} units of {req.blood_group} provided.")
        else:
            req.status = 'Pending'
            req.admin_message = (
                f"⚠️ Not enough {req.blood_group} stock available. "
                f"Requested: {units}, Available: {stock.units}. Please try again later."
            )
            messages.warning(request, f"⚠️ Not enough {req.blood_group} stock available. Request kept pending.")
            req.save()
            return redirect('admin_blood_request')

    stock.save()
    req.save()
    return redirect('admin_blood_request')

@login_required
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

@login_required
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

@login_required
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

@login_required
def hospital_request_history(request):
    requests = BloodRequest.objects.filter(user=request.user, role='Hospital')
    return render(request, 'hospital/hospital_request_history.html', {'requests': requests})

@login_required
def hospital_stock(request):
    stocks = BloodStock.objects.all()
    blood_data = {group: 0 for group, _ in BloodStock.BLOOD_GROUPS}
    for stock in stocks:
        blood_data[stock.blood_group] = stock.units
    context = {bg.lower().replace('+', '_positive').replace('-', '_negative'): units for bg, units in blood_data.items()}
    return render(request, 'hospital/hospital_stocks.html', context)

# Admin User Management

@login_required
def admin_donors(request):
    donors = DonorForm.objects.all().order_by('-id')
    return render(request, 'admin/admin_donors.html', {'donors': donors})

@login_required
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

@login_required
def admin_donor_list(request):
    donor_data = DonorForm.objects.all().order_by('-id')
    donors = Credential.objects.filter(role='Donor').select_related('user')
    return render(request, 'admin/admin_donors_list.html', {'donordata': donor_data, 'donors': donors})

@login_required
def admin_patients(request):
    patients = Credential.objects.filter(role='Patient').select_related('user')
    return render(request, 'admin/admin_patients.html', {'patients': patients})

@login_required
def admin_hospitals(request):
    hospitals = Credential.objects.filter(role='Hospital').select_related('user')
    return render(request, 'admin/admin_hospitals.html', {'hospitals': hospitals})

@login_required
def admin_profile(request):
    if not request.user.is_superuser:
        return redirect('home')
    return render(request, 'admin/admin_profile.html', {'user': request.user})


@login_required
def hospital_profile_view(request):
    hospital = HospitalDetails.objects.first()
    return render(request, 'hospital/hospital_profile_view.html', {'hospital': hospital})


@login_required
def hospital_profile(request):
    hospital = HospitalDetails.objects.first()

    if request.method == 'POST':
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospital profile saved successfully!")
            return redirect('hospitalhome') 
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = HospitalForm(instance=hospital)

    return render(request, 'hospital/hospital_details.html', {
        'form': form,
        'hospital': hospital
    })

@login_required
def patient_profile(request):
    try:
        profile = PatientProfile.objects.get(user=request.user)
    except PatientProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile)
        if form.is_valid():
            patient_profile = form.save(commit=False)
            patient_profile.user = request.user
            patient_profile.save()
            messages.success(request, "Profile saved successfully!")
            return redirect('patienthome')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PatientProfileForm(instance=profile)

    return render(request, 'patient/patient_profile.html', {'form': form, 'profile': profile})

@login_required
def patient_profile_view(request):
    profile = PatientProfile.objects.filter(user=request.user).first()
    return render(request, 'patient/patient_profile_view.html', {'profile': profile})

# @login_required
# def donor_profile(request):
#     profile, _ = DonorProfile.objects.get_or_create(user=request.user)

#     if request.method == 'POST':
#         form = DonorProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Donor profile saved successfully!")
#             return redirect('donorhome')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = DonorProfileForm(instance=profile)

#     return render(request, 'donor/donor_profile.html', {'form': form, 'profile': profile})


# @login_required
# def donor_profile_view(request):
#     try:
#         profile = DonorProfile.objects.get(user=request.user)
#     except DonorProfile.DoesNotExist:
#         profile = None  # Profile not created yet

#     return render(request, 'donor/donor_profile_view.html', {'profile': profile})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DonorProfile
from .forms import DonorProfileForm

@login_required
def donor_profile(request):
    profile, _ = DonorProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = DonorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Donor profile saved successfully!")
            return redirect('donorhome')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DonorProfileForm(instance=profile)

    return render(request, 'donor/donor_profile.html', {'form': form, 'profile': profile})

@login_required
def donor_profile_view(request):
    try:
        profile = DonorProfile.objects.get(user=request.user)
    except DonorProfile.DoesNotExist:
        profile = None

    return render(request, 'donor/donor_profile_view.html', {'profile': profile})