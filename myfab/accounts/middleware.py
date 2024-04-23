from django.shortcuts import redirect
from django.urls import reverse

class AdminRedirect:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("Request path:", request.path)
        if request.path.startswith('/admin/') and not request.user.is_superuser and request.user.is_authenticated:
            print("Redirecting non-superuser from admin page to home page.")
            return redirect(reverse('user:user_home'))
        
        response = self.get_response(request)
        return response