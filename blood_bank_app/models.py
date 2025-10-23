from django.db import models
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from django.conf import settings

User = get_user_model()

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]

class Credential(models.Model):
    ROLE_CHOICES = [
        ('Donor','Donor'),
        ('Patient','Patient'),
        ('Hospital','Hospital'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Donor')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credential')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class BloodStock(models.Model):
    BLOOD_GROUP = BLOOD_GROUP_CHOICES
    blood_group = models.CharField(max_length=5,choices=BLOOD_GROUP_CHOICES, unique=True)
    units = models.PositiveIntegerField(default=0)
    collected_date = models.DateField(default=date.today)
    expiry_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk: 
            self.collected_date = date.today()
            self.expiry_date = self.collected_date + timedelta(days=35)
        else:
            old_stock = BloodStock.objects.filter(pk=self.pk).first()
            if old_stock and old_stock.units != self.units:
                self.collected_date = date.today()
                self.expiry_date = self.collected_date + timedelta(days=35)
        super().save(*args, **kwargs)

    def is_expired(self):
        return date.today() > self.expiry_date if self.expiry_date else False

    def is_near_expiry(self):
        if self.expiry_date:
            return 0 <= (self.expiry_date - date.today()).days <= 5
        return False

    def __str__(self):
        return f"{self.blood_group} ({self.units} units)"


class DonorForm(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='donor_requests' 
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_donor_requests'
    )
    firstname = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    age = models.PositiveIntegerField(default=18)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    units = models.PositiveIntegerField()
    GENDER_CHOICES = [
        ('Male','Male'),
        ('Female','Female'),

    ]
    GENDER_CHOICES = [('Male','Male'), ('Female','Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    last_donate_date = models.DateTimeField(null=True, blank=True)
    last_receive_date = models.DateTimeField(null=True, blank=True)
    consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')




class BloodRequest(models.Model):
    ROLE_CHOICES = [('Patient', 'Patient'), ('Hospital', 'Hospital')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fname = models.CharField(max_length=100)
    email = models.EmailField()
    phonenum = models.CharField(max_length=15)
    age = models.PositiveIntegerField()
    reason = models.TextField()
    blood_group = models.CharField(max_length=5)
    units = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Patient')
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    admin_message = models.TextField(blank=True, null=True) 

    def __str__(self):
        return f"{self.fname} ({self.blood_group}) - {self.status}"

class HospitalDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
    
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20)
    blood_group = models.CharField(max_length=5)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.full_name

class DonorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    date_of_birth = models.DateField(help_text="Donor must be 18-65 years old")
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    
    height = models.FloatField(help_text="Height in centimeters")
    weight = models.FloatField(help_text="Weight in kilograms")
    bmi = models.FloatField(blank=True, null=True)
    hemoglobin = models.FloatField(help_text="Hemoglobin in g/dL",  default=13.0)

    systolic_pressure = models.PositiveIntegerField(help_text="Systolic BP in mmHg", default=120)
    diastolic_pressure = models.PositiveIntegerField(help_text="Diastolic BP in mmHg", default=80)
    blood_sugar = models.FloatField(help_text="Blood sugar in mg/dL", default=100)
    cholesterol = models.FloatField(help_text="Cholesterol in mg/dL",  default=200)
    
    taking_medicine = models.BooleanField(default=False)
    medicine_details = models.TextField(blank=True, null=True, help_text="Specify medicine and related disease if taking any")
    
    last_donated_date = models.DateField(blank=True, null=True)
    donation_count = models.PositiveIntegerField(default=0)
    available_status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default.jpg',
        blank=True,
        null=True
    )

    def calculate_bmi(self):
        try:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 2)
        except (ZeroDivisionError, TypeError):
            return None

    def save(self, *args, **kwargs):
        self.bmi = self.calculate_bmi()
        self.check_eligibility()
        super().save(*args, **kwargs)

    def check_eligibility(self):
        age = (date.today() - self.date_of_birth).days // 365
        if age < 18 or age > 65:
            self.available_status = False
            return
        if self.weight < 50:
            self.available_status = False
            return
        if self.gender == 'Male' and self.hemoglobin < 13:
            self.available_status = False
            return
        if self.gender == 'Female' and self.hemoglobin < 12.5:
            self.available_status = False
            return
        if not (100 <= self.systolic_pressure <= 180) or not (50 <= self.diastolic_pressure <= 100):
            self.available_status = False
            return
        if self.blood_sugar > 200:
            self.available_status = False
            return
        if self.cholesterol > 200:
            self.available_status = False
            return
        if self.last_donated_date and (date.today() - self.last_donated_date) < timedelta(days=90):
            self.available_status = False
            return
        self.available_status = True

    def __str__(self):
        return f"{self.name} ({self.blood_group})"
