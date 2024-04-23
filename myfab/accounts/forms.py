# forms.py
from django import forms
from .models import CustomUser
import re
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password



class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(max_length=254)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=13)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']

############################# Check email already exist ###################################
    def clean_email(self):
        email = self.cleaned_data.get('email')
        validator = EmailValidator(message='Enter a valid email address.')
        validator(email)
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    
############################# Check passwords ###################################
    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Both passwords should be same')
    
############################# Check phone number already exist ###################################
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match("^\d+$", phone_number):
            raise forms.ValidationError('Phone number should contain only digits.')
        if len(phone_number) > 10 or len(phone_number) < 10:
            raise forms.ValidationError('Phone number should have 10 digits')
        if not phone_number.startswith("+91"):
            phone_number = "+91" + phone_number
        return phone_number


############################# set user name as email before saving ###################################
    def save(self):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['email'] 
        password = self.cleaned_data['password1']
        user.set_password(password)
        user.save()
        return user

