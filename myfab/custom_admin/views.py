from django.shortcuts import render, redirect 
from django.http import JsonResponse
import json
from django.http import HttpResponse
from django.views import View
from accounts.models import CustomUser


# Create your views here.

class AdminHome(View):
    def get(self, request):
        users = CustomUser.objects.all()[:5]
        context = {'users': users}
        return render(request, 'admin_home.html', context)
    
    def post(self, request):
        print("Post data is:", request.body)
        json_data = json.loads(request.body)
        print("json data is:", json_data)

        if 'user_id' in json_data:  # Check for user_id in json data
                user_id = json_data.get('user_id')
                is_active = json_data.get('is_active') == 'on'  # Convert to boolean
                print("user_id and Is_active from json data is:", user_id, is_active)
                try:
                    user = CustomUser.objects.get(id=user_id)
                    user.is_active = is_active
                    user.save()
                    print("New status saved  for the user is", user.is_active)
                    return JsonResponse({'success': True})
                except CustomUser.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'User not found'})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
        else:
            print('Missing user_id in request data')
            return JsonResponse({'success': False, 'error': 'Missing user_id in request data'})




    
