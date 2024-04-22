from django.urls import path
from .views import Signup, LoginPage

urlpatterns = [
    path('login/', LoginPage.as_view(), name = 'login'),
    path('signup/', Signup.as_view(), name = 'signup')
]