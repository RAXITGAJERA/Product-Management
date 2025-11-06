from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import re
from inventory.models import UserProfile

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        self.restricted_paths = [
            '/products/create/',
            '/products/.*?/update/',
            '/products/.*?/delete/',
            '/categories/create/',
            '/categories/.*?/update/',
            '/categories/.*?/delete/',
            '/subcategories/create/',
            '/subcategories/.*?/update/',
            '/subcategories/.*?/delete/',
        ]
        
        self.public_paths = [
            '/login/',
            '/register/',
            '/admin/',
        ]

    def __call__(self, request):
        if not request.user.is_authenticated:
            if not any(request.path.startswith(path) for path in self.public_paths):
                messages.warning(request, 'Please log in to access this page.')
                return redirect(f"{reverse('login')}?next={request.path}")
        
        elif hasattr(request.user, 'userprofile'):
            user_role = request.user.userprofile.user_type
            
            for pattern in self.restricted_paths:
                if re.match(pattern, request.path):
                    if user_role not in ['admin', 'seller']:
                        messages.error(request, 'You do not have permission to access this page.')
                        return redirect('home')
                    break
        
        response = self.get_response(request)
        return response


class UserProfileCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not hasattr(request.user, 'userprofile'):
                UserProfile.objects.create(
                    user=request.user,
                    user_type='customer'
                )
        
        response = self.get_response(request)
        return response
