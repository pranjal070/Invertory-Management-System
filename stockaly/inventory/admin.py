from django.contrib import admin
from .models import CustomUser, InventoryItem


@admin.register(CustomUser)
class CustomUser(admin.ModelAdmin):
    list_display = ('email', 'username','role')
    search_fields = ('email', 'username','role')
    list_filter = ('role',)
    

admin.site.register(InventoryItem)