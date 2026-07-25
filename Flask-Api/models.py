# flask_api/models.py
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    inventory_items = db.relationship('InventoryItem', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_number = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_changed = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    history = db.relationship('InventoryItemHistory', backref='item', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'item_number': self.item_number,
            'quantity': self.quantity,
            'price': self.price,
            'date_added': self.date_added.strftime('%Y-%m-%d') if self.date_added else None,
            'last_changed': self.last_changed.isoformat() if self.last_changed else None,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None
        }

class InventoryItemHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'), nullable=False)
    old_quantity = db.Column(db.Integer, nullable=True)
    new_quantity = db.Column(db.Integer, nullable=True)
    old_price = db.Column(db.Float, nullable=True)
    new_price = db.Column(db.Float, nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    changed_by = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'old_quantity': self.old_quantity,
            'new_quantity': self.new_quantity,
            'old_price': self.old_price,
            'new_price': self.new_price,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'changed_by': self.changed_by.to_dict() if self.changed_by else None
        }

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(20), default='other')
    status = db.Column(db.String(20), default='active')
    website = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    products = db.relationship('SupplierProduct', backref='supplier', lazy=True, cascade="all, delete-orphan")
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'category': self.category,
            'status': self.status,
            'website': self.website,
            'notes': self.notes,
            'date_added': self.date_added.isoformat() if self.date_added else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class SupplierProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    unit_price = db.Column(db.Float, nullable=False)
    minimum_order_quantity = db.Column(db.Integer, default=1)
    lead_time_days = db.Column(db.Integer, default=7)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'product_name': self.product_name,
            'product_code': self.product_code,
            'description': self.description,
            'unit_price': self.unit_price,
            'minimum_order_quantity': self.minimum_order_quantity,
            'lead_time_days': self.lead_time_days,
            'is_active': self.is_active
        }

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    expected_delivery_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='draft')
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True, cascade="all, delete-orphan")
    created_by = db.relationship('User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'order_number': self.order_number,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'status': self.status,
            'total_amount': self.total_amount,
            'shipping_address': self.shipping_address,
            'notes': self.notes,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PurchaseOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('supplier_product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('SupplierProduct')
    
    def to_dict(self):
        return {
            'id': self.id,
            'purchase_order_id': self.purchase_order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price
        }