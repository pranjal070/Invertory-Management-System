from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import User, Supplier, SupplierProduct, PurchaseOrder, PurchaseOrderItem, db
from sqlalchemy import func

supplier_bp = Blueprint('supplier', __name__)

def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'admin'

@supplier_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def supplier_dashboard():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    total_suppliers = Supplier.query.count()
    active_suppliers = Supplier.query.filter_by(status='active').count()
    total_products = SupplierProduct.query.count()
    pending_orders = PurchaseOrder.query.filter(PurchaseOrder.status.in_(['draft', 'submitted'])).count()
    recent_suppliers = Supplier.query.order_by(Supplier.date_added.desc()).limit(5).all()
    recent_orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).limit(5).all()
    categories = db.session.query(
        Supplier.category,
        func.count(Supplier.id).label('count')
    ).group_by(Supplier.category).order_by(func.count(Supplier.id).desc()).all()
    categories_data = [{'category': category, 'count': count} for category, count in categories]
    return jsonify({
        'total_suppliers': total_suppliers,
        'active_suppliers': active_suppliers,
        'total_products': total_products,
        'pending_orders': pending_orders,
        'recent_suppliers': [supplier.to_dict() for supplier in recent_suppliers],
        'recent_orders': [order.to_dict() for order in recent_orders],
        'categories': categories_data
    }), 200

@supplier_bp.route('/', methods=['GET'])
@jwt_required()
def get_suppliers():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    query = Supplier.query
    if search_query:
        query = query.filter(
            (Supplier.name.ilike(f'%{search_query}%')) |
            (Supplier.company.ilike(f'%{search_query}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    suppliers = query.order_by(Supplier.name).all()
    return jsonify({
        'suppliers': [supplier.to_dict() for supplier in suppliers],
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter
    }), 200

@supplier_bp.route('/', methods=['POST'])
@jwt_required()
def add_supplier():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    data = request.get_json()
    supplier = Supplier(
        name=data['name'],
        company=data['company'],
        email=data['email'],
        phone=data['phone'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code'],
        country=data['country'],
        category=data.get('category', 'other'),
        status=data.get('status', 'active'),
        website=data.get('website'),
        notes=data.get('notes'),
    )
    db.session.add(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier added successfully', 'supplier': supplier.to_dict()}), 201

@supplier_bp.route('/<int:supplier_id>', methods=['GET'])
@jwt_required()
def get_supplier(supplier_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404
    products = SupplierProduct.query.filter_by(supplier_id=supplier_id).all()
    purchase_orders = PurchaseOrder.query.filter_by(supplier_id=supplier_id).order_by(PurchaseOrder.order_date.desc()).all()
    return jsonify({
        'supplier': supplier.to_dict(),
        'products': [product.to_dict() for product in products],
        'purchase_orders': [order.to_dict() for order in purchase_orders]
    }), 200

@supplier_bp.route('/<int:supplier_id>', methods=['PUT'])
@jwt_required()
def update_supplier(supplier_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    data = request.get_json()
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404
    supplier.name = data['name']
    supplier.company = data['company']
    supplier.email = data['email']
    supplier.phone = data['phone']
    supplier.address = data['address']
    supplier.city = data['city']
    supplier.state = data['state']
    supplier.zip_code = data['zip_code']
    supplier.country = data['country']
    supplier.category = data.get('category', 'other')
    supplier.status = data.get('status', 'active')
    supplier.website = data.get('website')
    supplier.notes = data.get('notes')
    supplier.last_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Supplier updated successfully', 'supplier': supplier.to_dict()}), 200

@supplier_bp.route('/<int:supplier_id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(supplier_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier deleted successfully'}), 200

@supplier_bp.route('/<int:supplier_id>/products', methods=['POST'])
@jwt_required()
def add_supplier_product(supplier_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404
    data = request.get_json()
    product = SupplierProduct(
        supplier_id=supplier_id,
        product_name=data['product_name'],
        product_code=data['product_code'],
        description=data.get('description'),
        unit_price=data['unit_price'],
        minimum_order_quantity=data.get('minimum_order_quantity', 1),
        lead_time_days=data.get('lead_time_days', 7),
        is_active=data.get('is_active', True)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully', 'product': product.to_dict()}), 201

@supplier_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_supplier_product(product_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    product = SupplierProduct.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    data = request.get_json()
    product.product_name = data['product_name']
    product.product_code = data['product_code']
    product.description = data.get('description')
    product.unit_price = data['unit_price']
    product.minimum_order_quantity = data.get('minimum_order_quantity', 1)
    product.lead_time_days = data.get('lead_time_days', 7)
    product.is_active = data.get('is_active', True)
    db.session.commit()
    return jsonify({'message': 'Product updated successfully', 'product': product.to_dict()}), 200

@supplier_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_supplier_product(product_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    product = SupplierProduct.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200

@supplier_bp.route('/purchase-orders', methods=['GET'])
@jwt_required()
def get_purchase_orders():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    query = PurchaseOrder.query
    if search_query:
        query = query.filter(
            (PurchaseOrder.order_number.ilike(f'%{search_query}%')) |
            (PurchaseOrder.supplier.has(Supplier.name.ilike(f'%{search_query}%')))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.order_by(PurchaseOrder.order_date.desc()).all()
    return jsonify({
        'orders': [order.to_dict() for order in orders],
        'search_query': search_query,
        'status_filter': status_filter
    }), 200

@supplier_bp.route('/purchase-orders', methods=['POST'])
@jwt_required()
def add_purchase_order():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    data = request.get_json()
    order = PurchaseOrder(
        supplier_id=data['supplier_id'],
        order_number=data['order_number'],
        order_date=datetime.strptime(data['order_date'], '%Y-%m-%d').date(),
        expected_delivery_date=datetime.strptime(data['expected_delivery_date'], '%Y-%m-%d').date(),
        status=data.get('status', 'draft'),
        total_amount=data['total_amount'],
        shipping_address=data['shipping_address'],
        notes=data.get('notes'),
        created_by_id=user_id
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Purchase order created successfully', 'order': order.to_dict()}), 201

@supplier_bp.route('/purchase-orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_purchase_order(order_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    order = PurchaseOrder.query.get(order_id)
    if not order:
        return jsonify({'error': 'Purchase order not found'}), 404
    items = PurchaseOrderItem.query.filter_by(purchase_order_id=order_id).all()
    return jsonify({
        'order': {
            **order.to_dict(),
            'supplier_name': order.supplier.name if order.supplier else None
        },
        'items': [item.to_dict() for item in items]
    }), 200

@supplier_bp.route('/purchase-orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_purchase_order(order_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    order = PurchaseOrder.query.get(order_id)
    if not order:
        return jsonify({'error': 'Purchase order not found'}), 404
    data = request.get_json()
    order.supplier_id = data['supplier_id']
    order.order_number = data['order_number']
    order.order_date = datetime.strptime(data['order_date'], '%Y-%m-%d').date()
    order.expected_delivery_date = datetime.strptime(data['expected_delivery_date'], '%Y-%m-%d').date()
    order.status = data.get('status', 'draft')
    order.total_amount = data['total_amount']
    order.shipping_address = data['shipping_address']
    order.notes = data.get['notes']
    db.session.commit()
    return jsonify({'message': 'Purchase order updated successfully', 'order': order.to_dict()}), 200

@supplier_bp.route('/purchase-orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_purchase_order(order_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    order = PurchaseOrder.query.get(order_id)
    if not order:
        return jsonify({'error': 'Purchase order not found'}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Purchase order deleted successfully'}), 200

@supplier_bp.route('/purchase-orders/<int:order_id>/items', methods=['POST'])
@jwt_required()
def add_order_item(order_id):
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    order = PurchaseOrder.query.get(order_id)
    if not order:
        return jsonify({'error': 'Purchase order not found'}), 404
    data = request.get_json()
    item = PurchaseOrderItem(
        purchase_order_id=order_id,
        product_id=data['product_id'],
        quantity=data['quantity'],
        unit_price=data['unit_price'],
        total_price=data['quantity'] * data['unit_price']
    )
    db.session.add(item)
    order.total_amount = db.session.query(func.sum(PurchaseOrderItem.total_price)).filter_by(purchase_order_id=order_id).scalar() or 0
    db.session.commit()
    return jsonify({'message': 'Item added to purchase order', 'item': item.to_dict()}), 201

@supplier_bp.route('/export', methods=['GET'])
@jwt_required()
def export_suppliers():
    user_id = get_jwt_identity()
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    suppliers = Supplier.query.all()
    export_data = []
    for supplier in suppliers:
        export_data.append({
            'name': supplier.name,
            'company': supplier.company,
            'email': supplier.email,
            'phone': supplier.phone,
            'address': supplier.address,
            'city': supplier.city,
            'state': supplier.state,
            'zip_code': supplier.zip_code,
            'country': supplier.country,
            'category': supplier.category,
            'status': supplier.status,
            'website': supplier.website
        })
    return jsonify({'data': export_data}), 200