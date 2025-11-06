def user_role_processor(request):
    context = {}
    
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        context['user_role'] = request.user.userprofile.user_type
        context['is_admin'] = request.user.userprofile.user_type == 'admin'
        context['is_seller'] = request.user.userprofile.user_type == 'seller'
        context['is_customer'] = request.user.userprofile.user_type == 'customer'
        context['can_add'] = request.user.userprofile.user_type in ['admin', 'seller']
        context['can_edit'] = request.user.userprofile.user_type in ['admin', 'seller']
        context['can_delete'] = request.user.userprofile.user_type in ['admin', 'seller']
    else:
        context['user_role'] = None
        context['is_admin'] = False
        context['is_seller'] = False
        context['is_customer'] = False
        context['can_add'] = False
        context['can_edit'] = False
        context['can_delete'] = False
    
    return context