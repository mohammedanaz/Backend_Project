# forms.py
from django import forms
from .models import CustomUser



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
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    
############################# Check phone number already exist ###################################
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('This phone number is already in use.')
        if len(phone_number) > 10 or len(phone_number) < 10:
            raise forms.ValidationError('Phone number should have 10 digits')
        if not phone_number.startswith("+91"):
            phone_number = "+91" + phone_number
        return phone_number


############################# set user name as email before saving ###################################
    def save(self):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['email'] 
        user.save()
        return user

