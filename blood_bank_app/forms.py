from django import forms
from django.contrib.auth import get_user_model
from .models import Credential, DonorForm, HospitalDetails, PatientProfile, DonorProfile
from django import forms
from datetime import date, timedelta

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=Credential.ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'role-choice'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control mb-3'})
        self.fields['email'].widget.attrs.update({'class': 'form-control mb-3'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class DonorFormForm(forms.ModelForm):
    class Meta:
        model = DonorForm
        fields = [
            'firstname', 'email', 'phone', 'age', 'blood_group',
            'units', 'gender', 'last_donate_date', 'last_receive_date', 'consent'
        ]



class HospitalForm(forms.ModelForm):
    class Meta:
        model = HospitalDetails
        fields = ['name', 'address', 'email', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'full_name',
            'age',
            'gender',
            'blood_group',
            'phone_number',
            'address',
            'profile_picture',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(
                attrs={'class': 'form-control'},
                choices=[
                    ('Male', 'Male'),
                    ('Female', 'Female'),
                    ('Other', 'Other'),
                ]
            ),
            'blood_group': forms.Select(
                attrs={'class': 'form-control'},
                choices=[
                    ('A+', 'A+'), ('A-', 'A-'),
                    ('B+', 'B+'), ('B-', 'B-'),
                    ('AB+', 'AB+'), ('AB-', 'AB-'),
                    ('O+', 'O+'), ('O-', 'O-'),
                ]
            ),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class DonorBasicForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = ['name', 'age', 'gender', 'blood_group', 'phone_number', 'address', 'profile_picture']
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class DonorEligibilityForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = [
            'date_of_birth', 'gender', 'weight', 'hemoglobin', 
            'systolic_pressure', 'diastolic_pressure', 
            'blood_sugar', 'cholesterol', 'last_donated_date'
        ]

    def clean(self):
        cleaned_data = super().clean()
        errors = {}

        dob = cleaned_data.get('date_of_birth')
        if dob:
            age = (date.today() - dob).days // 365
            if age < 18 or age > 65:
                errors['date_of_birth'] = "Donor must be between 18 and 65 years old."

        weight = cleaned_data.get('weight')
        if weight and weight < 50:
            errors['weight'] = "Donor must weigh at least 50 kg."

        gender = cleaned_data.get('gender')
        hemoglobin = cleaned_data.get('hemoglobin')
        if gender == 'Male' and hemoglobin and hemoglobin < 13:
            errors['hemoglobin'] = "Male donors must have hemoglobin >= 13 g/dL."
        if gender == 'Female' and hemoglobin and hemoglobin < 12.5:
            errors['hemoglobin'] = "Female donors must have hemoglobin >= 12.5 g/dL."

        sys = cleaned_data.get('systolic_pressure')
        dia = cleaned_data.get('diastolic_pressure')
        if sys and dia:
            if not (100 <= sys <= 180) or not (50 <= dia <= 100):
                errors['systolic_pressure'] = "Blood pressure must be within normal range."
                errors['diastolic_pressure'] = "Blood pressure must be within normal range."

        sugar = cleaned_data.get('blood_sugar')
        if sugar and sugar > 200:
            errors['blood_sugar'] = "Blood sugar must be <= 200 mg/dL."

        chol = cleaned_data.get('cholesterol')
        if chol and chol > 200:
            errors['cholesterol'] = "Cholesterol must be <= 200 mg/dL."

        last_donated = cleaned_data.get('last_donated_date')
        if last_donated and (date.today() - last_donated) < timedelta(days=90):
            errors['last_donated_date'] = "At least 90 days must pass since the last donation."

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data
