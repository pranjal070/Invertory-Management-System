from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
import csv
from datetime import datetime
from io import StringIO
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

from .forms import CustomUserCreationForm, InventoryItemForm, InventoryItemEditForm
from .api_client import APIClient

FLASK_API_BASE_URL = "http://127.0.0.1:5000/api/inventory"  # Updated to match the Flask API's inventory endpoint

# Store tokens in session
def get_api_client(request):
    token = request.session.get('access_token')
    return APIClient(token)

def home(request):
    return render(request, 'home.html')

def aboutus(request):
    return render(request, 'aboutus.html')

def index(request):
    # Check if user is logged in
    if 'access_token' not in request.session:
        messages.error(request, "Please login to access the dashboard")
        return redirect('login')
    
    # Check if this is a new user's first login
    is_new_user = request.session.get('is_new_user', False)
    
    sort_by = request.GET.get('sort_by', 'date_added')
    order = request.GET.get('order', 'asc')
    search_query = request.GET.get('search', '')
    
    # Get inventory items from API
    api_client = get_api_client(request)
    response, status_code = api_client.get_inventory_items(sort_by, order, search_query)
    
    # Log the API response for debugging
    logging.debug(f"API Response: {response}")
    logging.debug(f"Status Code: {status_code}")
    
    if status_code != 200:
        messages.error(request, f"Error fetching inventory items: {response.get('error', 'Unknown error')}")
        items = []
    else:
        items = response.get('items', [])
    
    # Log the fetched items
    logging.debug(f"Fetched items for index view: {items}")
    
    # Log the structure of the items data
    if items:
        logging.debug(f"Sample item structure: {items[0]}")
    
    context = {
        'items': items,
        'mode': 'index',
        'sort_by': sort_by,
        'order': order,
        'search_query': search_query,
        'form': InventoryItemForm(),
        'is_new_user': is_new_user
    }
    
    # Log the items being passed to the template
    logging.debug(f"Items passed to template: {items}")
    
    # Clear the new user flag after first view
    if is_new_user:
        request.session['is_new_user'] = False
    
    return render(request, 'index.html', context)

def add_item(request):
    # Check if user is logged in
    if 'access_token' not in request.session:
        messages.error(request, "Please login to add items")
        return redirect('login')
    
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            # Add item via API
            api_client = get_api_client(request)
            response, status_code = api_client.add_inventory_item(
                form.cleaned_data['item_name'],
                form.cleaned_data['item_number'],
                form.cleaned_data['quantity'],
                form.cleaned_data['price']
            )
            
            # Log the API response for debugging
            logging.debug(f"API Response: {response}")
            logging.debug(f"Status Code: {status_code}")
            
            if status_code == 201:
                messages.success(request, 'Item added successfully!')
            else:
                messages.error(request, f"Error adding item: {response.get('error', 'Unknown error')}")
            
            return redirect('index')
        else:
            messages.error(request, 'Error adding item. Please check the form.')
    
    return redirect('index')

def view_item(request, id):
    # Check if user is logged in
    if 'access_token' not in request.session:
        messages.error(request, "Please login to view items")
        return redirect('login')
    
    # Get item from API
    api_client = get_api_client(request)
    response, status_code = api_client.get_inventory_item(id)
    
    # Log the API response for debugging
    logging.debug(f"API Response: {response}")
    logging.debug(f"Status Code: {status_code}")
    
    if status_code != 200:
        messages.error(request, f"Error fetching item: {response.get('error', 'Unknown error')}")
        return redirect('index')
    
    item = response.get('item', {})
    
    return render(request, 'view_item.html', {'item': item})

def edit_item(request, id):
    # Check if user is logged in
    if 'access_token' not in request.session:
        messages.error(request, "Please login to edit items")
        return redirect('login')
    
    api_client = get_api_client(request)
    
    if request.method == 'POST':
        form = InventoryItemEditForm(request.POST)
        if form.is_valid():
            # Update item via API
            response, status_code = api_client.update_inventory_item(
                id,
                form.cleaned_data['item_name'],
                form.cleaned_data['item_number'],
                form.cleaned_data['quantity'],
                form.cleaned_data['price']
            )
            
            # Log the API response for debugging
            logging.debug(f"API Response: {response}")
            logging.debug(f"Status Code: {status_code}")
            
            if status_code == 200:
                if response.get('message') == 'Nothing has been changed':
                    messages.info(request, 'Nothing has been changed')
                else:
                    messages.success(request, 'Item updated successfully!')
            else:
                messages.error(request, f"Error updating item: {response.get('error', 'Unknown error')}")
            
            return redirect('index')
        else:
            messages.error(request, 'Error updating item. Please check the form.')
    else:
        # Get item from API for editing
        response, status_code = api_client.get_inventory_item(id)
        
        # Log the API response for debugging
        logging.debug(f"API Response: {response}")
        logging.debug(f"Status Code: {status_code}")
        
        if status_code != 200:
            messages.error(request, f"Error fetching item: {response.get('error', 'Unknown error')}")
            return redirect('index')
        
        item = response.get('item', {})
        form = InventoryItemEditForm(initial=item)
    
    return render(request, 'index.html', {'item': item, 'mode': 'edit', 'form': form})

def delete_item(request, id):
    # Check if user is logged in
    if 'access_token' not in request.session:
        messages.error(request, "Please login to delete items")
        return redirect('login')
    
    # Delete item via API
    api_client = get_api_client(request)
    response, status_code = api_client.delete_inventory_item(id)
    
    # Log the API response for debugging
    logging.debug(f"API Response: {response}")
    logging.debug(f"Status Code: {status_code}")
    
    if status_code == 200:
        messages.success(request, 'Item deleted successfully!')
    else:
        messages.error(request, f"Error deleting item: {response.get('error', 'Unknown error')}")
    
    return redirect('index')

def export_csv(request):
    # Check if user is logged in
    if 'access_token' not in request.session:
        messages.error(request, "Please login to export data")
        return redirect('login')
    
    # Export inventory via API
    api_client = get_api_client(request)
    response, status_code = api_client.export_inventory_csv()
    
    # Log the API response for debugging
    logging.debug(f"API Response: {response}")
    logging.debug(f"Status Code: {status_code}")
    
    if status_code != 200:
        messages.error(request, f"Error exporting inventory: {response.get('error', 'Unknown error')}")
        return redirect('index')
    
    export_data = response.get('data', [])
    
    # Create CSV response
    http_response = HttpResponse(content_type='text/csv')
    http_response['Content-Disposition'] = 'attachment; filename="inventory.csv"'
    
    writer = csv.writer(http_response)
    writer.writerow(['Date Added', 'Item Name', 'Item Number', 'Quantity', 'Price', 'Last Changed'])
    
    for item in export_data:
        writer.writerow([
            item['date_added'],
            item['item_name'],
            item['item_number'],
            item['quantity'],
            item['price'],
            item['last_changed']
        ])
    
    return http_response

def role_required(request, role):
    # Check if user is logged in
    if 'access_token' not in request.session:
        return False
    
    # Check user role via API
    api_client = get_api_client(request)
    response, status_code = api_client.get_user_profile()
    
    # Log the API response for debugging
    logging.debug(f"API Response: {response}")
    logging.debug(f"Status Code: {status_code}")
    
    if status_code != 200 or response.get('user', {}).get('role') != role:
        return False
    return True

def admin_dashboard(request):
    # Check if user is logged in and has admin role
    if not role_required(request, "admin"):
        messages.error(request, "Unauthorized Access. Please login as admin.")
        return redirect('login')
    
    sort_by = request.GET.get('sort_by', 'date_added')
    order = request.GET.get('order', 'asc')
    search_query = request.GET.get('search', '')
    user_filter = request.GET.get('user_filter', 'all')
    
    # Get admin dashboard data from API
    api_client = get_api_client(request)
    response, status_code = api_client.get_admin_dashboard(sort_by, order, search_query, user_filter)
    
    # Log the API response for debugging
    logging.debug(f"API Response: {response}")
    logging.debug(f"Status Code: {status_code}")
    
    if status_code != 200:
        messages.error(request, f"Error fetching admin dashboard: {response.get('error', 'Unknown error')}")
        return redirect('index')
    
    context = {
        'items': response.get('items', []),
        'all_users': response.get('all_users', []),
        'user_count': response.get('user_count', 0),
        'mode': 'admin',
        'sort_by': sort_by,
        'order': order,
        'search_query': search_query,
        'user_filter': user_filter
    }
    
    return render(request, 'admin_dashboard.html', context)

def admin_edit_item(request, id):
    # Check if user is logged in and has admin role
    if not role_required(request, "admin"):
        messages.error(request, "Unauthorized Access. Please login as admin.")
        return redirect('login')
    
    api_client = get_api_client(request)
    
    if request.method == 'POST':
        form = InventoryItemEditForm(request.POST)
        if form.is_valid():
            # Update item via API
            response, status_code = api_client.admin_edit_item(
                id,
                form.cleaned_data['item_name'],
                form.cleaned_data['item_number'],
                form.cleaned_data['quantity'],
                form.cleaned_data['price']
            )
            
            # Log the API response for debugging
            logging.debug(f"API Response: {response}")
            logging.debug(f"Status Code: {status_code}")
            
            if status_code == 200:
                if response.get('message') == 'Nothing has been changed':
                    messages.info(request, 'Nothing has been changed')
                else:
                    messages.success(request, 'Item updated successfully!')
            else:
                messages.error(request, f"Error updating item: {response.get('error', 'Unknown error')}")
            
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Error updating item. Please check the form.')
    else:
        # Get item from API for editing
        response, status_code = api_client.get_inventory_item(id)
        
        # Log the API response for debugging
        logging.debug(f"API Response: {response}")
        logging.debug(f"Status Code: {status_code}")
        
        if status_code != 200:
            messages.error(request, f"Error fetching item: {response.get('error', 'Unknown error')}")
            return redirect('admin_dashboard')
        
        item = response.get('item', {})
        form = InventoryItemEditForm(initial=item)
    
    return render(request, 'admin_edit_item.html', {'form': form, 'item': item})

def admin_delete_item(request, id):
    # Check if user is logged in and has admin role
    if not role_required(request, "admin"):
        messages.error(request, "Unauthorized Access. Please login as admin.")
        return redirect('login')
    
    # Delete item via API
    api_client = get_api_client(request)
    response, status_code = api_client.admin_delete_item(id)
    
    # Log the API response for debugging
    logging.debug(f"API Response: {response}")
    logging.debug(f"Status Code: {status_code}")
    
    if status_code == 200:
        messages.success(request, 'Item deleted successfully!')
    else:
        messages.error(request, f"Error deleting item: {response.get('error', 'Unknown error')}")
    
    return redirect('admin_dashboard')

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Register user via API
            api_client = APIClient()  # No token needed for registration
            response, status_code = api_client.register_user(
                form.cleaned_data['username'],
                form.cleaned_data['email'],
                form.cleaned_data['password1'],
                form.cleaned_data.get('role', 'user')
            )
            
            # Log the API response for debugging
            logging.debug(f"API Response: {response}")
            logging.debug(f"Status Code: {status_code}")
            
            if status_code == 201:
                messages.success(request, "Registration successful! Please login with your credentials.")
                # Redirect to login page after successful registration
                return redirect('login')
            else:
                messages.error(request, f"Registration error: {response.get('error', 'Unknown error')}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Login user via API
        api_client = APIClient()  # No token needed for login
        response, status_code = api_client.login_user(username, password)
        
        # Log the API response for debugging
        logging.debug(f"API Response: {response}")
        logging.debug(f"Status Code: {status_code}")
        
        if status_code == 200:
            # Store token and user info in session
            request.session['access_token'] = response.get('access_token')
            user = response.get('user', {})
            request.session['user_role'] = user.get('role', 'user')
            request.session['username'] = user.get('username', '')
            
            # Check if this is a new user
            is_new_user = (datetime.now() - datetime.fromisoformat(user.get('date_joined', datetime.now().isoformat()))).total_seconds() < 300
            request.session['is_new_user'] = is_new_user
            
            if user.get('role') == "admin":
                messages.success(request, f"Welcome back, {username}! You are logged in as admin.")
                return redirect('admin_dashboard')
            else:
                messages.success(request, f"Welcome back, {username}! You are logged in successfully.")
                return redirect('index')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    
    return render(request, 'login.html')

def logout_user(request):
    # Clear all session data
    request.session.flush()
    messages.success(request, "You have been logged out successfully")
    return redirect('home')

def profile(request):
    # Check if user is logged in
    if 'access_token' not in request.session:
        messages.error(request, "Please login to view your profile")
        return redirect('login')
    
    # Get user profile from API
    api_client = get_api_client(request)
    response, status_code = api_client.get_user_profile()
    
    # Log the API response for debugging
    logging.debug(f"API Response: {response}")
    logging.debug(f"Status Code: {status_code}")
    
    if status_code != 200:
        messages.error(request, f"Error fetching profile: {response.get('error', 'Unknown error')}")
        return redirect('index')
    
    user = response.get('user', {})
    
    return render(request, 'profile.html', {'user': user})

def dashboard_charts(request):
    # Check if user is logged in
    if 'access_token' not in request.session:
        messages.error(request, "Please login to view analytics")
        return redirect('login')

    # Fetch inventory items from Flask API
    try:
        response = requests.get(f"{FLASK_API_BASE_URL}/", headers={"Authorization": f"Bearer {request.session['access_token']}"})
        response.raise_for_status()
        items = response.json().get('items', [])

        # Log the fetched items
        logging.debug(f"Fetched items from Flask API: {items}")
    except requests.RequestException as e:
        messages.error(request, f"Error fetching inventory items: {e}")
        items = []

    # Calculate statistics for the dashboard
    total_items = len(items)
    total_quantity = sum(item.get('quantity', 0) for item in items)
    total_value = sum(item.get('quantity', 0) * item.get('price', 0) for item in items)
    total_value = round(total_value, 2)
    low_stock_count = sum(1 for item in items if item.get('quantity', 0) < 10)

    # Log the fetched items for debugging
    logging.debug(f"Fetched items for analytics: {items}")

    # Log calculated statistics
    logging.debug(f"Total items: {total_items}, Total quantity: {total_quantity}, Total value: {total_value}, Low stock count: {low_stock_count}")

    context = {
        'total_items': total_items,
        'total_quantity': total_quantity,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'items': items
    }

    return render(request, 'dashboard_charts.html', context)

def error_404(request, exception):
    return render(request, "errorPages/404.html", status=404)

def error_500(request):
    return render(request, "errorPages/500.html", status=500)
