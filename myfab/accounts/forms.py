# forms.py
from django import forms
from .models import CustomUser, Address
from orders.models import ReturnOrder, Order
import re
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import make_password
import requests
import phonenumbers


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
        if not re.match(r"^\d+$", phone_number):
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


############################# Add Address Form ###########################################
class AddressForm(forms.ModelForm):
    '''
    Form To add new user address. clean_pincode() checks for valid india post pincode. 
    '''
    class Meta:
        model = Address
        fields = ['customer_id', 'name', 'house_name', 'street_name_1', 'street_name_2', 
                  'city', 'state', 'pincode', 'phone_number']

    def clean_pincode(self):
        '''
        clean_pincode() checks for valid india post pincode. 
        '''
        pincode = self.cleaned_data['pincode']
        response = requests.get('https://api.postalpincode.in/pincode/'+pincode)
        if response.status_code == 200:
            data = response.json()
            first_result = data[0]  # Assuming the first item contains relevant data
            if first_result.get('Status') == 'Success':
                return pincode
            else:
                raise forms.ValidationError('Invalid Pincode')
        else:
            print('Invalid Response')
            raise forms.ValidationError('Error validating Pincode')
        
    def clean_phone_number(self):
        """
        Validate and format the phone number using phonenumbers library.
        """
        phone_number = self.cleaned_data['phone_number']
        if phone_number:
            try:
                parsed_number = phonenumbers.parse(phone_number, "IN")
                if not phonenumbers.is_valid_number(parsed_number):
                    raise forms.ValidationError('Invalid phone number')
            except phonenumbers.phonenumberutil.NumberParseException:
                raise forms.ValidationError('Invalid phone number format')
        return phone_number


######################## Form for request return order ##########################

class ReturnOrderForm(forms.ModelForm):
    '''
    Form To create an instance of Return Order model.
    '''
    class Meta:
        model = ReturnOrder
        fields = ['order_id', 'reason', 'image_1', 'image_2']

    def clean(self):
        cleaned_data = super().clean()
        
        order = cleaned_data.get('order_id')
        image_1 = cleaned_data.get('image_1')
        image_2 = cleaned_data.get('image_2')

        if ReturnOrder.objects.filter(order_id=order).exists():
            print('Some issue in the comparing order ids')
            self.add_error('order_id', "Already made a return request for this order.")
            return cleaned_data
        
        if image_1 and image_1.size > 2 * 1024 * 1024:  # 2 MB limit
            self.add_error('image_1', "Image 1 file size should be less than 2 MB.")
        
        if image_2 and image_2.size > 2 * 1024 * 1024:  # 2 MB limit
            self.add_error('image_2', "Image 2 file size should be less than 2 MB.")
        
        return cleaned_data
