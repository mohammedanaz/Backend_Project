import requests
import random
from decimal import Decimal

################### Function to send OTP ############################
def send_otp(phone_number, otp):
    url = "https://instantalerts.co/api/web/send"
    params = {
        'apikey': '621492a44a89m36c2209zs4l7e74672cj',
        'sender':  'SEDEMO',
        'to': phone_number,
        'message': f'Hello {otp}, This is a test message from spring edge '
    }
    response = requests.post(url, data=params)
    print(response.text)  # Print the response for reference


################### Function to generate OTP ############################
def generate_otp():
    return str(random.randint(100000, 999999))


################### Function to validate input Qty and Measurements #########################
def validate_input(value):
    '''
    Check if measurement_value is a valid number and greater than 0.
    Since the input field is number type only string '' or 'e' possible.
    '''
    if value  and value != 'e':
        decimal_value = Decimal(value)
        if decimal_value > 0:
            return True
        else:
            return False
    else:
        return False
