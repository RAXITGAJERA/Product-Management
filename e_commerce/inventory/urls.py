from django.urls import path
from inventory import views

urlpatterns = [
    path('', views.home_view, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update_view, name='profile_update'),
    path('password/change/', views.password_change_view, name='password_change'),

    path('categories/', views.category_list_view, name='category_list'),
    path('categories/<int:pk>/', views.category_detail_view, name='category_detail'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update_view, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),

    path('subcategories/', views.subcategory_list_view, name='subcategory_list'),
    path('subcategories/<int:pk>/', views.subcategory_detail_view, name='subcategory_detail'),
    path('subcategories/create/', views.subcategory_create_view, name='subcategory_create'),
    path('subcategories/<int:pk>/update/', views.subcategory_update_view, name='subcategory_update'),
    path('subcategories/<int:pk>/delete/', views.subcategory_delete_view, name='subcategory_delete'),

    path('products/', views.product_list_view, name='product_list'),
    path('products/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('products/create/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/update/', views.product_update_view, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),
]
