from django.urls import path
from .views import UserHome

urlpatterns = [
    path('', UserHome.as_view(), name = 'user_home'),
]