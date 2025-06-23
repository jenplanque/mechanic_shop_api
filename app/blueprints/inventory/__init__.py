from flask import Blueprint

inventory_items_bp = Blueprint("inventory_items_bp", __name__)

from . import routes  # Import routes to register them with the blueprint
