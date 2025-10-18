from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]

class Donor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    units = models.PositiveIntegerField()
    donation_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.blood_group})"
    
class Credential(models.Model):
    ROLE_CHOICES = [
        ('Donor','Donor'),
        ('Patient','Patient'),
        ('Hospital','Hospital'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=10,choices=ROLE_CHOICES,default='Donor')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credential')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class BloodStock(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, unique=True)
    units = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blood_group} - {self.units} units"

class DonorForm(models.Model):
    firstname = models.TextField(max_length=20)
    email = models.EmailField(max_length=50) 
    phone = models.CharField(max_length=15)
    age = models.PositiveIntegerField(default=18)  
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    units = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]) 
    last_donate_date = models.DateField(null=True, blank=True)
    last_receive_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.firstname
    
class RequestForm(models.Model):
    firstname = models.TextField(max_length=20)
    email = models.EmailField(max_length=50) 
    phone = models.CharField(max_length=15)
    age = models.PositiveIntegerField()
    reason = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=5,choices=BLOOD_GROUP_CHOICES)
    units = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
    ])

    def __str__(self):
        return self.firstname

class HospitalRequestForm(models.Model):
    hospitalname = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=120)
    blood_group = models.CharField(max_length=5,choices=BLOOD_GROUP_CHOICES)
    units = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.hospitalname