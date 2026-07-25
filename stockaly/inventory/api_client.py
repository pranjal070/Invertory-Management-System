import requests
import json
import decimal
from django.conf import settings

# Flask API base URL
API_BASE_URL = 'http://localhost:5000/api'

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class APIClient:
    def __init__(self, token=None):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json'
        }
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
    
    def register_user(self, username, email, password, role='user'):
        url = f'{API_BASE_URL}/auth/register'
        data = {
            'username': username,
            'email': email,
            'password': password,
            'role': role
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def login_user(self, username, password):
        url = f'{API_BASE_URL}/auth/login'
        data = {
            'username': username,
            'password': password
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def get_user_profile(self):
        url = f'{API_BASE_URL}/auth/profile'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    # Inventory Items
    def get_inventory_items(self, sort_by='date_added', order='asc', search=''):
        url = f'{API_BASE_URL}/inventory/?sort_by={sort_by}&order={order}&search={search}'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    def add_inventory_item(self, item_name, item_number, quantity, price):
        url = f'{API_BASE_URL}/inventory/'
        data = {
            'item_name': item_name,
            'item_number': item_number,
            'quantity': quantity,
            'price': price
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def get_inventory_item(self, item_id):
        url = f'{API_BASE_URL}/inventory/{item_id}'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    def update_inventory_item(self, item_id, item_name, item_number, quantity, price):
        url = f'{API_BASE_URL}/inventory/{item_id}'
        data = {
            'item_name': item_name,
            'item_number': item_number,
            'quantity': quantity,
            'price': price
        }
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def delete_inventory_item(self, item_id):
        url = f'{API_BASE_URL}/inventory/{item_id}'
        response = requests.delete(url, headers=self.headers)
        return response.json(), response.status_code
    
    def export_inventory_csv(self):
        url = f'{API_BASE_URL}/inventory/export'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    # Admin Dashboard
    def get_admin_dashboard(self, sort_by='date_added', order='asc', search='', user_filter='all'):
        url = f'{API_BASE_URL}/admin/dashboard?sort_by={sort_by}&order={order}&search={search}&user_filter={user_filter}'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    def admin_edit_item(self, item_id, item_name, item_number, quantity, price):
        url = f'{API_BASE_URL}/admin/items/{item_id}'
        data = {
            'item_name': item_name,
            'item_number': item_number,
            'quantity': quantity,
            'price': price
        }
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def admin_delete_item(self, item_id):
        url = f'{API_BASE_URL}/admin/items/{item_id}'
        response = requests.delete(url, headers=self.headers)
        return response.json(), response.status_code
    
    # Supplier Management
    def get_supplier_dashboard(self):
        url = f'{API_BASE_URL}/suppliers/dashboard'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    def get_suppliers(self, search='', status='', category=''):
        url = f'{API_BASE_URL}/suppliers/?search={search}&status={status}&category={category}'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    def add_supplier(self, data):
        url = f'{API_BASE_URL}/suppliers/'
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def get_supplier(self, supplier_id):
        url = f'{API_BASE_URL}/suppliers/{supplier_id}'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    def update_supplier(self, supplier_id, data):
        url = f'{API_BASE_URL}/suppliers/{supplier_id}'
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def delete_supplier(self, supplier_id):
        url = f'{API_BASE_URL}/suppliers/{supplier_id}'
        response = requests.delete(url, headers=self.headers)
        return response.json(), response.status_code
    
    def add_supplier_product(self, supplier_id, data):
        url = f'{API_BASE_URL}/suppliers/{supplier_id}/products'
        response = requests.post(url, headers=self.headers, data=json.dumps(data, cls=DecimalEncoder))
        return response.json(), response.status_code
    
    def update_supplier_product(self, product_id, data):
        url = f'{API_BASE_URL}/suppliers/products/{product_id}'
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def delete_supplier_product(self, product_id):
        url = f'{API_BASE_URL}/suppliers/products/{product_id}'
        response = requests.delete(url, headers=self.headers)
        return response.json(), response.status_code
    
    def get_purchase_orders(self, search='', status=''):
        url = f'{API_BASE_URL}/suppliers/purchase-orders?search={search}&status={status}'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    def add_purchase_order(self, data):
        url = f'{API_BASE_URL}/suppliers/purchase-orders'
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def get_purchase_order(self, order_id):
        url = f'{API_BASE_URL}/suppliers/purchase-orders/{order_id}'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    def update_purchase_order(self, order_id, data):
        url = f'{API_BASE_URL}/suppliers/purchase-orders/{order_id}'
        response = requests.put(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def delete_purchase_order(self, order_id):
        url = f'{API_BASE_URL}/suppliers/purchase-orders/{order_id}'
        response = requests.delete(url, headers=self.headers)
        return response.json(), response.status_code
    
    def add_order_item(self, order_id, data):
        url = f'{API_BASE_URL}/suppliers/purchase-orders/{order_id}/items'
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        return response.json(), response.status_code
    
    def export_suppliers_csv(self):
        url = f'{API_BASE_URL}/suppliers/export'
        response = requests.get(url, headers=self.headers)
        return response.json(), response.status_code
    
    
# Add this function at the end
def get_api_client(request=None):
    token = None
    if request and hasattr(request, 'session'):
        token = request.session.get('access_token')
    return APIClient(token=token)
