from django import forms
from django.contrib.auth import get_user_model
from .models import Credential, DonorForm

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



class HospitalForm(forms.ModelForm):
    hospitalname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phonenumber = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
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

    def clean(self):
        data = super().clean()
        password = data.get('password')
        confirm = data.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match")
        return data

    def save(self, commit=True):
        hospital = super().save(commit=False)
        hospital.set_password(self.cleaned_data['password'])
        if commit:
            hospital.save()
        return hospital



class DonorFormForm(forms.ModelForm):
    class Meta:
        model = DonorForm
        fields = [
            'firstname', 'email', 'phone', 'age', 'blood_group',
            'units', 'gender', 'last_donate_date', 'last_receive_date', 'consent'
        ]

