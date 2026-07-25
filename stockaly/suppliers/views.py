from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import csv
from datetime import datetime
from inventory.api_client import get_api_client
from .forms import SupplierForm, SupplierProductForm, PurchaseOrderForm, PurchaseOrderItemForm

def supplier_dashboard(request):
    api_client = get_api_client(request)
    response, status_code = api_client.get_supplier_dashboard()
    if status_code != 200:
        messages.error(request, f"Error fetching supplier dashboard: {response.get('error', 'Unknown error')}")
        return redirect('index')
    context = {
        'total_suppliers': response.get('total_suppliers', 0),
        'active_suppliers': response.get('active_suppliers', 0),
        'total_products': response.get('total_products', 0),
        'pending_orders': response.get('pending_orders', 0),
        'recent_suppliers': response.get('recent_suppliers', []),
        'recent_orders': response.get('recent_orders', []),
        'categories': response.get('categories', []),
    }
    return render(request, 'suppliers/supplier_dashboard.html', context)

def supplier_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    api_client = get_api_client(request)
    response, status_code = api_client.get_suppliers(search_query, status_filter, category_filter)
    if status_code != 200:
        messages.error(request, f"Error fetching suppliers: {response.get('error', 'Unknown error')}")
        suppliers = []
    else:
        suppliers = response.get('suppliers', [])
    context = {
        'suppliers': suppliers,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    return render(request, 'suppliers/supplier_list.html', context)

def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            api_client = get_api_client(request)
            response, status_code = api_client.add_supplier(form.cleaned_data)
            if status_code == 201:
                messages.success(request, 'Supplier added successfully!')
                return redirect('supplier_list')
            else:
                messages.error(request, f"Error adding supplier: {response.get('error', 'Unknown error')}")
    else:
        form = SupplierForm()
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': 'Add Supplier'})

def edit_supplier(request, pk):
    api_client = get_api_client(request)
    response, status_code = api_client.get_supplier(pk)
    if status_code != 200:
        messages.error(request, f"Error fetching supplier: {response.get('error', 'Unknown error')}")
        return redirect('supplier_list')
    supplier = response.get('supplier', {})
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            response, status_code = api_client.update_supplier(pk, form.cleaned_data)
            if status_code == 200:
                messages.success(request, 'Supplier updated successfully!')
                return redirect('supplier_list')
            else:
                messages.error(request, f"Error updating supplier: {response.get('error', 'Unknown error')}")
    else:
        form = SupplierForm(initial=supplier)
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})

def delete_supplier(request, pk):
    api_client = get_api_client(request)
    response, status_code = api_client.get_supplier(pk)
    if status_code != 200:
        messages.error(request, f"Error fetching supplier: {response.get('error', 'Unknown error')}")
        return redirect('supplier_list')
    supplier = response.get('supplier', {})
    if request.method == 'POST':
        response, status_code = api_client.delete_supplier(pk)
        if status_code == 200:
            messages.success(request, 'Supplier deleted successfully!')
            return redirect('supplier_list')
        else:
            messages.error(request, f"Error deleting supplier: {response.get('error', 'Unknown error')}")
    return render(request, 'suppliers/confirm_delete.html', {'supplier': supplier})

def supplier_detail(request, pk):
    api_client = get_api_client(request)
    response, status_code = api_client.get_supplier(pk)
    if status_code != 200:
        messages.error(request, f"Error fetching supplier: {response.get('error', 'Unknown error')}")
        return redirect('supplier_list')
    context = {
        'supplier': response.get('supplier', {}),
        'products': response.get('products', []),
        'purchase_orders': response.get('purchase_orders', []),
    }
    return render(request, 'suppliers/supplier_detail.html', context)

def add_supplier_product(request, supplier_id):
    api_client = get_api_client(request)
    response, status_code = api_client.get_supplier(supplier_id)
    if status_code != 200:
        messages.error(request, f"Error fetching supplier: {response.get('error', 'Unknown error')}")
        return redirect('supplier_list')
    supplier = response.get('supplier', {})
    if request.method == 'POST':
        form = SupplierProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            response, status_code = api_client.add_supplier_product(supplier_id, data)
            if status_code == 201:
                messages.success(request, 'Product added successfully!')
                return redirect('supplier_detail', pk=supplier_id)
            else:
                messages.error(request, f"Error adding product: {response.get('error', 'Unknown error')}")
    else:
        form = SupplierProductForm()
    return render(request, 'suppliers/product_form.html', {
        'form': form, 
        'title': f'Add Product for {supplier.get("name")}',
        'supplier': supplier
    })

def edit_supplier_product(request, pk):
    api_client = get_api_client(request)
    product = {'id': pk}
    supplier_id = 0
    if request.method == 'POST':
        form = SupplierProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            response, status_code = api_client.update_supplier_product(pk, data)
            if status_code == 200:
                messages.success(request, 'Product updated successfully!')
                return redirect('supplier_detail', pk=supplier_id)
            else:
                messages.error(request, f"Error updating product: {response.get('error', 'Unknown error')}")
    else:
        form = SupplierProductForm(initial=product)
    return render(request, 'suppliers/product_form.html', {
        'form': form, 
        'title': 'Edit Product',
        'supplier': {'id': supplier_id}
    })

def delete_supplier_product(request, pk):
    api_client = get_api_client(request)
    product = {'id': pk, 'supplier': {'id': 0}}
    if request.method == 'POST':
        response, status_code = api_client.delete_supplier_product(pk)
        if status_code == 200:
            messages.success(request, 'Product deleted successfully!')
            return redirect('supplier_detail', pk=product['supplier']['id'])
        else:
            messages.error(request, f"Error deleting product: {response.get('error', 'Unknown error')}")
    return render(request, 'suppliers/confirm_delete_product.html', {'product': product})

def purchase_order_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    api_client = get_api_client(request)
    response, status_code = api_client.get_purchase_orders(search_query, status_filter)
    if status_code != 200:
        messages.error(request, f"Error fetching purchase orders: {response.get('error', 'Unknown error')}")
        orders = []
    else:
        orders = response.get('orders', [])
    context = {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'suppliers/purchase_order_list.html', context)

def add_purchase_order(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            api_client = get_api_client(request)
            response, status_code = api_client.add_purchase_order(form.cleaned_data)
            if status_code == 201:
                messages.success(request, 'Purchase order created successfully!')
                return redirect('purchase_order_detail', pk=response.get('order', {}).get('id'))
            else:
                messages.error(request, f"Error creating purchase order: {response.get('error', 'Unknown error')}")
    else:
        form = PurchaseOrderForm()
    return render(request, 'suppliers/purchase_order_form.html', {'form': form, 'title': 'Create Purchase Order'})

def edit_purchase_order(request, pk):
    api_client = get_api_client(request)
    response, status_code = api_client.get_purchase_order(pk)
    if status_code != 200:
        messages.error(request, f"Error fetching purchase order: {response.get('error', 'Unknown error')}")
        return redirect('purchase_order_list')
    order = response.get('order', {})
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            response, status_code = api_client.update_purchase_order(pk, form.cleaned_data)
            if status_code == 200:
                messages.success(request, 'Purchase order updated successfully!')
                return redirect('purchase_order_detail', pk=pk)
            else:
                messages.error(request, f"Error updating purchase order: {response.get('error', 'Unknown error')}")
    else:
        form = PurchaseOrderForm(initial=order)
    return render(request, 'suppliers/purchase_order_form.html', {'form': form, 'title': 'Edit Purchase Order'})

def delete_purchase_order(request, pk):
    api_client = get_api_client(request)
    response, status_code = api_client.get_purchase_order(pk)
    if status_code != 200:
        messages.error(request, f"Error fetching purchase order: {response.get('error', 'Unknown error')}")
        return redirect('purchase_order_list')
    order = response.get('order', {})
    if request.method == 'POST':
        response, status_code = api_client.delete_purchase_order(pk)
        if status_code == 200:
            messages.success(request, 'Purchase order deleted successfully!')
            return redirect('purchase_order_list')
        else:
            messages.error(request, f"Error deleting purchase order: {response.get('error', 'Unknown error')}")
    return render(request, 'suppliers/confirm_delete_order.html', {'order': order})

def purchase_order_detail(request, pk):
    api_client = get_api_client(request)
    response, status_code = api_client.get_purchase_order(pk)
    if status_code != 200:
        messages.error(request, f"Error fetching purchase order: {response.get('error', 'Unknown error')}")
        return redirect('purchase_order_list')
    context = {
        'order': response.get('order', {}),
        'items': response.get('items', []),
        'supplier_name': response.get('order', {}).get('supplier_name', 'Unknown Supplier')
    }
    return render(request, 'suppliers/purchase_order_detail.html', context)

def add_order_item(request, order_id):
    api_client = get_api_client(request)
    response, status_code = api_client.get_purchase_order(order_id)
    if status_code != 200:
        messages.error(request, f"Error fetching purchase order: {response.get('error', 'Unknown error')}")
        return redirect('purchase_order_list')
    order = response.get('order', {})
    if request.method == 'POST':
        form = PurchaseOrderItemForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            response, status_code = api_client.add_order_item(order_id, data)
            if status_code == 201:
                messages.success(request, 'Item added to purchase order!')
                return redirect('purchase_order_detail', pk=order_id)
            else:
                messages.error(request, f"Error adding item to purchase order: {response.get('error', 'Unknown error')}")
    else:
        form = PurchaseOrderItemForm()
    return render(request, 'suppliers/order_item_form.html', {
        'form': form, 
        'title': 'Add Item to Purchase Order',
        'order': order
    })

def export_suppliers_csv(request):
    api_client = get_api_client(request)
    response, status_code = api_client.export_suppliers_csv()
    if status_code != 200:
        messages.error(request, f"Error exporting suppliers: {response.get('error', 'Unknown error')}")
        return redirect('supplier_list')
    export_data = response.get('data', [])
    http_response = HttpResponse(content_type='text/csv')
    http_response['Content-Disposition'] = f'attachment; filename="suppliers_{datetime.now().strftime("%Y%m%d")}.csv"'
    writer = csv.writer(http_response)
    writer.writerow(['Name', 'Company', 'Email', 'Phone', 'Address', 'City', 'State', 'Zip', 'Country', 'Category', 'Status', 'Website'])
    for supplier in export_data:
        writer.writerow([
            supplier['name'],
            supplier['company'],
            supplier['email'],
            supplier['phone'],
            supplier['address'],
            supplier['city'],
            supplier['state'],
            supplier['zip_code'],
            supplier['country'],
            supplier['category'],
            supplier['status'],
            supplier['website']
        ])
    return http_response
