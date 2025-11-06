from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from inventory.models import UserProfile


class Command(BaseCommand):
    help = 'Create default user roles and groups'

    def handle(self, *args, **kwargs):
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        seller_group, _ = Group.objects.get_or_create(name='Seller')
        customer_group, _ = Group.objects.get_or_create(name='Customer')
        
        self.stdout.write(self.style.SUCCESS('Groups created successfully!'))
        
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            UserProfile.objects.create(user=admin_user, user_type='admin')
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('Admin user created!'))
        
        if not User.objects.filter(username='seller').exists():
            seller_user = User.objects.create_user('seller', 'seller@example.com', 'seller123')
            UserProfile.objects.create(user=seller_user, user_type='seller')
            seller_user.groups.add(seller_group)
            self.stdout.write(self.style.SUCCESS('Seller user created!'))
        
        if not User.objects.filter(username='customer').exists():
            customer_user = User.objects.create_user('customer', 'customer@example.com', 'customer123')
            UserProfile.objects.create(user=customer_user, user_type='customer')
            customer_user.groups.add(customer_group)
            self.stdout.write(self.style.SUCCESS('Customer user created!'))