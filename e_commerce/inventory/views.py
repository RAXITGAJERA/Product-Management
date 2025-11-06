from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from inventory.models import Category, SubCategory, Product, UserProfile
from inventory.forms import CategoryForm, SubCategoryForm, ProductForm, UserRegistrationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator


def is_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.user_type == 'admin'


def is_seller_or_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.user_type in ['admin', 'seller']


def is_customer(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.user_type == 'customer'


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                user_type=form.cleaned_data['role']
            )
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile_view(request):
    products_created = Product.objects.filter(created_by=request.user).count()
    days_active = (timezone.now().date() - request.user.date_joined.date()).days
    recent_products = Product.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    context = {
        'products_created': products_created,
        'days_active': days_active,
        'total_logins': 'N/A',
        'recent_products': recent_products,
    }
    return render(request, 'profile.html', context)


@login_required
def profile_update_view(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        messages.success(request, 'Profile updated successfully!')
    return redirect('profile')


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('profile')


def home_view(request):
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_subcategories': SubCategory.objects.count(),
        'low_stock_products': Product.objects.filter(stock__lte=10).count(),
    }
    
    if request.user.is_authenticated:
        context['user_role'] = request.user.userprofile.user_type
        context['recent_products'] = Product.objects.all().order_by('-created_at')[:5]
    
    return render(request, 'home.html', context)


@login_required
def category_list_view(request):
    categories = Category.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'can_add': is_seller_or_admin(request.user),
        'can_edit': is_seller_or_admin(request.user),
        'total_categories': Category.objects.count(),
        'total_subcategories': SubCategory.objects.count(),
        'total_products_in_categories': Product.objects.count(),
    }
    return render(request, 'category_list.html', context)


@login_required
def category_detail_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    subcategories = {}
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'can_add': is_seller_or_admin(request.user),
        'can_edit': is_seller_or_admin(request.user),
    }
    return render(request, 'category_detail.html', context)


@login_required
@user_passes_test(is_seller_or_admin, login_url='home')
def category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('category_detail', pk=category.pk)
    else:
        form = CategoryForm()
    
    context = {'form': form}
    return render(request, 'category_form.html', context)


@login_required
@user_passes_test(is_seller_or_admin, login_url='home')
def category_update_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('category_detail', pk=category.pk)
    else:
        form = CategoryForm(instance=category)
    
    context = {'form': form}
    return render(request, 'category_form.html', context)


@login_required
@user_passes_test(is_seller_or_admin, login_url='home')
def category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('category_list')
    
    context = {'category': category}
    return render(request, 'category_confirm_delete.html', context)


@login_required
def subcategory_list_view(request):
    subcategories = SubCategory.objects.select_related('category')
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        subcategories = subcategories.filter(category_id=category_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        subcategories = subcategories.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(subcategories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'subcategories': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'all_categories': Category.objects.all(),
        'can_add': is_seller_or_admin(request.user),
        'can_edit': is_seller_or_admin(request.user),
        'total_subcategories': SubCategory.objects.count(),
        'total_categories': Category.objects.count(),
        'total_products_in_subcategories': Product.objects.count(),
    }
    return render(request, 'subcategory_list.html', context)


@login_required
def subcategory_detail_view(request, pk):
    """View subcategory details"""
    subcategory = get_object_or_404(SubCategory, pk=pk)
    products = Product.objects.filter(subcategory=subcategory)
    
    # Calculate statistics
    total_value = sum(p.price * p.stock for p in products)
    average_price = products.aggregate(avg_price=Sum('price'))['avg_price'] or 0
    
    context = {
        'subcategory': subcategory,
        'products': products,
        'total_value': total_value,
        'average_price': average_price,
        'can_add': is_seller_or_admin(request.user),
        'can_edit': is_seller_or_admin(request.user),
    }
    return render(request, 'subcategory_detail.html', context)



@login_required
@user_passes_test(is_seller_or_admin, login_url='home')
def subcategory_create_view(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            subcategory = form.save(commit=False)
            subcategory.created_by = request.user
            subcategory.save()
            messages.success(request, f'Subcategory "{subcategory.name}" created successfully!')
            return redirect('subcategory_detail', pk=subcategory.pk)
    else:
        # Pre-select category if provided in URL
        initial = {}
        category_id = request.GET.get('category')
        if category_id:
            initial['category'] = category_id
        form = SubCategoryForm(initial=initial)
    
    context = {'form': form}
    return render(request, 'subcategory_form.html', context)


@login_required
@user_passes_test(is_seller_or_admin, login_url='home')
def subcategory_update_view(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subcategory "{subcategory.name}" updated successfully!')
            return redirect('subcategory_detail', pk=subcategory.pk)
    else:
        form = SubCategoryForm(instance=subcategory)
    
    context = {'form': form}
    return render(request, 'subcategory_form.html', context)


@login_required
@user_passes_test(is_seller_or_admin, login_url='home')
def subcategory_delete_view(request, pk):
    subcategory = get_object_or_404(SubCategory, pk=pk)
    
    if request.method == 'POST':
        subcategory_name = subcategory.name
        subcategory.delete()
        messages.success(request, f'Subcategory "{subcategory_name}" deleted successfully!')
        return redirect('subcategory_list')
    
    context = {'subcategory': subcategory}
    return render(request, 'subcategory_confirm_delete.html', context)



@login_required
def product_list_view(request):
    products = Product.objects.select_related('category', 'subcategory', 'created_by')
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    # Filter by subcategory
    subcategory_filter = request.GET.get('subcategory')
    if subcategory_filter:
        products = products.filter(subcategory_id=subcategory_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'all_categories': Category.objects.all(),
        'all_subcategories': SubCategory.objects.all(),
        'can_add': is_seller_or_admin(request.user),
        'can_edit': is_seller_or_admin(request.user),
        'user_role': request.user.userprofile.user_type,
        'total_products': Product.objects.count(),
        'low_stock_count': Product.objects.filter(stock__lte=10).count(),
        'out_of_stock_count': Product.objects.filter(stock=0).count(),
    }
    return render(request, 'product_list.html', context)


@login_required
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    total_value = product.price * product.stock

    context = {
        'product': product,
        'total_value': total_value,
        'can_edit': is_seller_or_admin(request.user) or product.created_by == request.user,
        'user_role': request.user.userprofile.user_type,
    }
    return render(request, 'product_detail.html', context)


@login_required
@user_passes_test(is_seller_or_admin, login_url='home')
def product_create_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        # Pre-select subcategory if provided in URL
        initial = {}
        subcategory_id = request.GET.get('subcategory')
        if subcategory_id:
            subcategory = get_object_or_404(SubCategory, pk=subcategory_id)
            initial['subcategory'] = subcategory
            initial['category'] = subcategory.category
        form = ProductForm(initial=initial)
    
    context = {'form': form}
    return render(request, 'product_form.html', context)


@login_required
@user_passes_test(is_seller_or_admin, login_url='home')
def product_update_view(request, pk):
    """Update an existing product"""
    product = get_object_or_404(Product, pk=pk)
    
    if not (is_seller_or_admin(request.user) or product.created_by == request.user):
        messages.error(request, 'You do not have permission to edit this product.')
        return redirect('product_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form}
    return render(request, 'product_form.html', context)



@login_required
@user_passes_test(is_seller_or_admin, login_url='home')
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if not (is_seller_or_admin(request.user) or product.created_by == request.user):
        messages.error(request, 'You do not have permission to delete this product.')
        return redirect('product_detail', pk=pk)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('product_list')
    
    context = {'product': product}
    return render(request, 'product_confirm_delete.html', context)
