from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import User, InventoryItem, db

admin_bp = Blueprint('admin', __name__)

def is_admin(user_id):
    user = User.query.get(user_id)
    return user and user.role == 'admin'

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get query parameters
    sort_by = request.args.get('sort_by', 'date_added')
    order = request.args.get('order', 'asc')
    search_query = request.args.get('search', '')
    user_filter = request.args.get('user_filter', 'all')
    
    # Base query - all items for admin
    query = InventoryItem.query
    
    # Filter by user if specified
    if user_filter != 'all':
        query = query.filter_by(user_id=user_filter)
    
    # Apply search filter
    if search_query:
        query = query.filter(
            (InventoryItem.item_name.ilike(f'%{search_query}%')) |
            (InventoryItem.item_number.ilike(f'%{search_query}%'))
        )
    
    # Apply sorting
    if sort_by == 'item_name':
        query = query.order_by(InventoryItem.item_name.asc() if order == 'asc' else InventoryItem.item_name.desc())
    elif sort_by == 'item_number':
        query = query.order_by(InventoryItem.item_number.asc() if order == 'asc' else InventoryItem.item_number.desc())
    elif sort_by == 'quantity':
        query = query.order_by(InventoryItem.quantity.asc() if order == 'asc' else InventoryItem.quantity.desc())
    elif sort_by == 'price':
        query = query.order_by(InventoryItem.price.asc() if order == 'asc' else InventoryItem.price.desc())
    elif sort_by == 'user':
        # This is more complex in SQLAlchemy, simplified here
        query = query.join(User).order_by(User.username.asc() if order == 'asc' else User.username.desc())
    else:
        query = query.order_by(InventoryItem.date_added.asc() if order == 'asc' else InventoryItem.date_added.desc())
    
    items = query.all()
    all_users = User.query.all()
    user_count = User.query.count()
    
    return jsonify({
        'items': [item.to_dict() for item in items],
        'all_users': [user.to_dict() for user in all_users],
        'user_count': user_count,
        'sort_by': sort_by,
        'order': order,
        'search_query': search_query,
        'user_filter': user_filter
    }), 200

@admin_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def admin_edit_item(item_id):
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    
    data = request.get_json()
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    # Check if anything changed
    if (data['item_name'] == item.item_name and
        data['item_number'] == item.item_number and
        int(data['quantity']) == item.quantity and
        float(data['price']) == item.price):
        return jsonify({'message': 'Nothing has been changed', 'item': item.to_dict()}), 200
    
    # Update item
    item.item_name = data['item_name']
    item.item_number = data['item_number']
    item.quantity = data['quantity']
    item.price = data['price']
    item.last_changed = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Item updated successfully', 'item': item.to_dict()}), 200

@admin_bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_item(item_id):
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    
    item = InventoryItem.query.get(item_id)
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message': 'Item deleted successfully'}), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    user_id = get_jwt_identity()
    
    if not is_admin(user_id):
        return jsonify({'error': 'Unauthorized access'}), 403
    
    users = User.query.all()
    
    return jsonify({'users': [user.to_dict() for user in users]}), 200