from django.contrib import admin
from inventory.models import Category, SubCategory, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_on', 'created_by']
    list_filter = ['is_active', 'created_on']
    search_fields = ['name', 'description']
    readonly_fields = ['created_on', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_on', 'created_by']
    list_filter = ['is_active', 'category', 'created_on']
    search_fields = ['name', 'description']
    readonly_fields = ['created_on', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'price', 'stock', 'created_at', 'created_by']
    list_filter = ['category', 'subcategory', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)