import requests
import random

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
