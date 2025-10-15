from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import Credential

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=Credential.ROLE_CHOICES)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].help_text = None

    def clean(self):
        data = super().clean()
        if data.get('password1') != data.get('password2'):
            raise forms.ValidationError("Passwords do not match")
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            Credential.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )
        return user

class HospitalRegistrationForm(forms.ModelForm):
    hospitalname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phonenumber = forms.CharField(max_length=15,widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'password1', 'password2']:
            if field_name in self.fields:
                self.fields[field_name].help_text = None

    def clean(self):
        """Validate matching passwords — silently ignore if not matching."""
        data = super().clean()
        password = data.get('password')
        confirm = data.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', None)
            data['confirm_password'] = ''
        return data

    def clean_hospitalname(self):
        """Ensure hospital name is provided (silent check)."""
        name = self.cleaned_data.get('hospitalname')
        if not name:
            self.add_error('hospitalname', None)
        return name

    def save(self, commit=True):
        """Save hospital user with encrypted password."""
        hospital = super().save(commit=False)
        hospital.set_password(self.cleaned_data['password'])
        if commit:
            hospital.save()
        return hospital

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


ROLE_CHOICES = [
    ('donor', 'Donor'),
    ('patient', 'Patient'),
]

# class RegistrationForm(forms.ModelForm):
#     username = forms.CharField(max_length=100)
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)
#     role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
#     phone = forms.CharField(max_length=15)
#     gender = forms.ChoiceField(choices=GENDER_CHOICES)
#     blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES)
#     address = forms.CharField(widget=forms.Textarea)
#     age = forms.IntegerField(required=False, label="Age (Donor only)")
#     required_units = forms.IntegerField(required=False, label="Required Units (Patient only)")
#     name = forms.CharField(required=False, label="Hospital Name (Hospital only)")

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password']

#     def clean(self):
#         cleaned_data = super().clean()
#         role = cleaned_data.get('role')
#         age = cleaned_data.get('age')
#         name = cleaned_data.get('name')

#         if role == 'donor' and not age:
#             self.add_error('age', 'Donor must provide age.')
#         elif role == 'hospital' and not name:
#             self.add_error('name', 'Hospital must provide a name.')

#         return cleaned_data


