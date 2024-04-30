from django.shortcuts import render, redirect 
from django.http import JsonResponse
import json
from django.views import View
from accounts.models import CustomUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.
################################### Admin Home ####################################
class AdminHome(View):
    def get(self, request):
        users = CustomUser.objects.all()[:5]
        context = {'users': users}
        return render(request, 'admin_home.html', context)
    
    def post(self, request):
        json_data = json.loads(request.body)

        if 'user_id' in json_data:  # Check for user_id in json data
                user_id = json_data.get('user_id')
                is_active = json_data.get('is_active')
                try:
                    user = CustomUser.objects.get(id=user_id)
                    user.is_active = is_active
                    user.save()
                    return JsonResponse({'success': True})
                except CustomUser.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'User not found'})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': str(e)})
        else:
            print('Missing user_id in request data')
            return JsonResponse({'success': False, 'error': 'Missing user_id in request data'})


################################### Admin Users ####################################

class AdminUsers(View):
    def get(self, request):
        users_list = CustomUser.objects.all()
        paginator = Paginator(users_list, 10) 
        page_number = request.GET.get('page')
        try:
            users = paginator.page(page_number)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        context = {'users': users}
        return render(request, 'admin_users.html', context)
