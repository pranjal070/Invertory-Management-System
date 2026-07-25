import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import InventoryItem, InventoryItemHistory, User, db

# Configure logging
logging.basicConfig(level=logging.DEBUG)

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/', methods=['GET'])
@jwt_required()
def get_inventory_items():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Log user ID and query parameters
    logging.debug(f"Fetching inventory items for user_id: {user_id}")

    # Get query parameters
    sort_by = request.args.get('sort_by', 'date_added')
    order = request.args.get('order', 'asc')
    search_query = request.args.get('search', '')

    # Base query
    query = InventoryItem.query.filter_by(user_id=user_id)

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
    else:
        query = query.order_by(InventoryItem.date_added.asc() if order == 'asc' else InventoryItem.date_added.desc())

    items = query.all()

    # Log fetched items
    logging.debug(f"Fetched items: {[item.to_dict() for item in items]}")

    return jsonify({
        'items': [item.to_dict() for item in items],
        'sort_by': sort_by,
        'order': order,
        'search_query': search_query
    }), 200

@inventory_bp.route('/', methods=['POST'])
@jwt_required()
def add_inventory_item():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data or not all(k in data for k in ['item_name', 'item_number', 'quantity', 'price']):
        logging.error(f"Missing required fields in data: {data}")
        return jsonify({'error': 'Missing required fields'}), 400
    
    item = InventoryItem(
        item_name=data['item_name'],
        item_number=data['item_number'],
        quantity=int(data['quantity']),
        price=float(data['price']),
        user_id=user_id
    )
    
    db.session.add(item)
    db.session.commit()
    
    logging.debug(f"Added item: {item.to_dict()}")
    return jsonify({'message': 'Item added successfully', 'item': item.to_dict()}), 201

@inventory_bp.route('/<int:item_id>', methods=['GET'])
@jwt_required()
def get_inventory_item(item_id):
    user_id = get_jwt_identity()
    
    # Log the item_id and user_id for debugging
    logging.debug(f"Fetching item with id: {item_id} for user_id: {user_id}")

    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    # Log the query result
    logging.debug(f"Query result: {item.to_dict() if item else 'Item not found'}")

    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify({'item': item.to_dict()}), 200

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_inventory_item(item_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate data
    if not data or not all(k in data for k in ['item_name', 'item_number', 'quantity', 'price']):
        logging.error(f"Missing required fields in data: {data}")
        return jsonify({'error': 'Missing required fields'}), 400
    
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        logging.debug(f"Item not found: id={item_id}, user_id={user_id}")
        return jsonify({'error': 'Item not found'}), 404
    
    # Check for changes
    old_quantity = item.quantity
    old_price = item.price
    changes = False
    
    if (data['item_name'] == item.item_name and
        data['item_number'] == item.item_number and
        int(data['quantity']) == item.quantity and
        float(data['price']) == item.price):
        logging.debug(f"No changes for item_id: {item_id}")
        return jsonify({'message': 'Nothing has been changed', 'item': item.to_dict()}), 200
    
    # Update item
    item.item_name = data['item_name']
    item.item_number = data['item_number']
    item.quantity = int(data['quantity'])
    item.price = float(data['price'])
    item.last_changed = datetime.utcnow()
    changes = True
    
    # Log changes to history if quantity or price changed
    if old_quantity != item.quantity or old_price != item.price:
        history_entry = InventoryItemHistory(
            item_id=item.id,
            old_quantity=old_quantity,
            new_quantity=item.quantity,
            old_price=old_price,
            new_price=item.price,
            changed_by_id=user_id,
            changed_at=datetime.utcnow()
        )
        db.session.add(history_entry)
        logging.debug(f"Logged history entry for item_id: {item_id}")
    
    db.session.commit()
    
    logging.debug(f"Updated item: {item.to_dict()}")
    return jsonify({'message': 'Item updated successfully', 'item': item.to_dict()}), 200

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_inventory_item(item_id):
    user_id = get_jwt_identity()
    
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        logging.debug(f"Item not found for deletion: id={item_id}, user_id={user_id}")
        return jsonify({'error': 'Item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    logging.debug(f"Deleted item_id: {item_id}")
    return jsonify({'message': 'Item deleted successfully'}), 200

@inventory_bp.route('/export', methods=['GET'])
@jwt_required()
def export_inventory():
    user_id = get_jwt_identity()
    
    items = InventoryItem.query.filter_by(user_id=user_id).all()
    
    export_data = []
    for item in items:
        export_data.append({
            'date_added': item.date_added.strftime('%Y-%m-%d') if item.date_added else '',
            'item_name': item.item_name,
            'item_number': item.item_number,
            'quantity': item.quantity,
            'price': item.price,
            'last_changed': item.last_changed.strftime('%Y/%m/%d') if item.last_changed else ''
        })
    
    logging.debug(f"Exported inventory for user_id: {user_id}")
    return jsonify({'data': export_data}), 200

@inventory_bp.route('/<int:item_id>/history', methods=['GET'])
@jwt_required()
def get_item_history(item_id):
    user_id = get_jwt_identity()
    
    # Log the item_id and user_id for debugging
    logging.debug(f"Fetching history for item_id: {item_id}, user_id: {user_id}")
    
    # Verify item exists and belongs to user
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        logging.debug(f"Item not found: id={item_id}, user_id={user_id}")
        return jsonify({'error': 'Item not found'}), 404
    
    # Fetch history entries, ordered by most recent
    history = InventoryItemHistory.query.filter_by(item_id=item_id).order_by(InventoryItemHistory.changed_at.desc()).all()
    
    # Log fetched history
    logging.debug(f"Fetched history: {[entry.to_dict() for entry in history]}")
    
    return jsonify({'history': [entry.to_dict() for entry in history]}), 200

@inventory_bp.route('/debug', methods=['GET'])
@jwt_required()
def debug_inventory_items():
    user_id = get_jwt_identity()
    items = InventoryItem.query.filter_by(user_id=user_id).all()
    return jsonify({'items': [item.to_dict() for item in items]})