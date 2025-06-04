from flask import Blueprint

mechanics_bp = Blueprint("mechanics_bp", __name__)

from . import routes  # Import routes to register them with the blueprint
