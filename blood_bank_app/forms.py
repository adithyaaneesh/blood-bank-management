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


class DonorFormForm(forms.ModelForm):
    class Meta:
        model = DonorForm
        fields = [
            'firstname', 'email', 'phone', 'age', 'blood_group',
            'units', 'gender', 'last_donate_date', 'last_receive_date', 'consent'
        ]

