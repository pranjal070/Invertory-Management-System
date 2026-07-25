# flask_api/__init__.py
from flask import Flask
from config import Config
from extensions import db, jwt, cors
import models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    # Import routes
    from routes.auth_routes import auth_bp
    from routes.inventory_routes import inventory_bp
    from routes.admin_routes import admin_bp
    from routes.supplier_routes import supplier_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(supplier_bp, url_prefix='/api/suppliers')
    
    @app.before_first_request
    def create_tables():
        db.create_all()
    
    return app