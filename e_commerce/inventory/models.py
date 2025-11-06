from django.db import models
from django.contrib.auth.models import User
from inventory.choices import user_type

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    user_type = models.CharField(choices=user_type, verbose_name="User type", null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class Category(models.Model):
    name = models.CharField(max_length=100, default="", verbose_name="Name")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['-created_on']


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    class Meta:
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"
        ordering = ['-created_on']
        

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']