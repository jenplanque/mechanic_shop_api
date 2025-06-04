from flask import Blueprint

service_tickets_bp = Blueprint("service_tickets_bp", __name__)

from . import routes  # Import routes to register them with the blueprint
