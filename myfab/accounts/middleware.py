from django.shortcuts import redirect
from django.urls import reverse

class AdminRedirect:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_url = reverse('admin:index')
        custom_admin_url = reverse('custom_admin:admin_home')

        # if request.path.startswith(custom_admin_url) and request.user.is_authenticated:
        #     print("Redirecting auth user to custom admin home page.")
        #     return redirect(reverse('custom_admin:admin_home'))
        # if request.path.startswith(custom_admin_url) and not request.user.is_authenticated:
        #     print("Redirecting non-auth user from custom admin page to login page.")
        #     return redirect(reverse('accounts:login'))
        if (request.path.startswith(admin_url) or request.path.startswith(custom_admin_url)) and not request.user.is_superuser and request.user.is_authenticated:
            print("Redirecting non-superuser from admin page to user home page.")
            return redirect(reverse('user:user_home'))
        
        response = self.get_response(request)
        return response