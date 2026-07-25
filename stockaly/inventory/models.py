from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile','user']

    def __str__(self):
        return self.email

class InventoryItem(models.Model):
    item_name = models.CharField(max_length=100)
    item_number = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.FloatField()
    date_added = models.DateTimeField(default=timezone.now)
    last_changed = models.DateTimeField(null=True, blank=True)
    # Add user field to associate items with specific users
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='inventory_items', null=True)

    def __str__(self):
        return self.item_name
    
    def total_value(self):
        return self.quantity * self.price