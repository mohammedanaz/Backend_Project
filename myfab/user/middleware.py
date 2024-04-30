from django.shortcuts import redirect
from django.urls import reverse

class UserHomeRedirect:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_home_url = reverse('user:user_home')
        
        if request.path.startswith(user_home_url) and not request.user.is_authenticated:
            return redirect(reverse('accounts:login'))  
        
        response = self.get_response(request)
        return response