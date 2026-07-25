from rest_framework import serializers
from .models import CustomUser, InventoryItem

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'date_joined', 'last_login']

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'item_name', 'item_number', 'quantity', 'price', 'date_added', 'last_changed', 'user']

class SupplierSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    company = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    city = serializers.CharField(max_length=50)
    state = serializers.CharField(max_length=50)
    zip_code = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=50)
    category = serializers.CharField(max_length=20)
    status = serializers.CharField(max_length=20)
    website = serializers.URLField(allow_null=True)
    notes = serializers.CharField(allow_null=True)
    date_added = serializers.DateTimeField(read_only=True)
    last_updated = serializers.DateTimeField(read_only=True)

class SupplierProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    supplier_id = serializers.IntegerField()
    product_name = serializers.CharField(max_length=100)
    product_code = serializers.CharField(max_length=50)
    description = serializers.CharField(allow_null=True)
    unit_price = serializers.FloatField()
    minimum_order_quantity = serializers.IntegerField()
    lead_time_days = serializers.IntegerField()
    is_active = serializers.BooleanField()

class PurchaseOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    supplier_id = serializers.IntegerField()
    order_number = serializers.CharField(max_length=50)
    order_date = serializers.DateField()
    expected_delivery_date = serializers.DateField()
    status = serializers.CharField(max_length=20)
    total_amount = serializers.FloatField()
    shipping_address = serializers.CharField()
    notes = serializers.CharField(allow_null=True)
    created_by_id = serializers.IntegerField(allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

class PurchaseOrderItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    purchase_order_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    unit_price = serializers.FloatField()
    total_price = serializers.FloatField()