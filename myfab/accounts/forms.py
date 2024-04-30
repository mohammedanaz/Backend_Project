# forms.py
from django import forms
from .models import CustomUser
import re
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password


############################# Signup form ###########################################
class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(max_length=254)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone_number = forms.CharField(max_length=13)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password', 'confirm_password']

######## overriding clean() to make confirm_password available in cleaned data dict ######
    def clean(self):
        cleaned_data = super().clean()  #calling parent clean() to run default validation and make cleaned data dict
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:                          #check both password matches
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data

######## Check email already exist ######
    def clean_email(self):
        email = self.cleaned_data.get('email')
        validator = EmailValidator(message='Enter a valid email address.')
        validator(email)
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    
###### Check passwords ##################
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8 :
            raise forms.ValidationError('Password must contain 8 characters')
        if not any(char.isupper() for char in password):
            raise forms.ValidationError('Password must contain at least one upper case')
        if not any(char.islower() for char in password):
            raise forms.ValidationError('Password must contain at least one lower case')
        if not any(char in '@/_' for char in password):
            raise forms.ValidationError('Password must contain any one special character from \'@/_\'')
        return password

    
####### Check phone number already exist #####
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match("^\d+$", phone_number):
            raise forms.ValidationError('Phone number should contain only digits.')
        if len(phone_number) > 10 or len(phone_number) < 10:
            raise forms.ValidationError('Phone number should have 10 digits')
        return phone_number


###### set user name as email before saving #####
    def save(self):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['email'] 
        password = self.cleaned_data['password']
        user.set_password(password)
        user.save()
        return user

############################# OTPVerificationForm ###########################################
class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6)




