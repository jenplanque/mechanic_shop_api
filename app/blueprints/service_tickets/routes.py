from .schemas import (
    service_ticket_schema,
    service_tickets_schema,
    edit_service_ticket_schema,
)
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, ServiceTicket, Customer, Mechanic, InventoryItem
from app.utils.util import token_required

# from app.extensions import limiter, cache
from . import service_tickets_bp


# ADD SERVICE TICKET
@service_tickets_bp.route("/", methods=["POST"])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    customer_id = service_ticket_data.get("customer_id")
    if not customer_id or not db.session.get(Customer, customer_id):
        return jsonify({"error": "Customer not found"}), 404

    new_service_ticket = ServiceTicket(**service_ticket_data)
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201


# GET ALL SERVICE TICKETS
@service_tickets_bp.route("/", methods=["GET"])
def get_all_service_tickets():
    query = select(ServiceTicket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200


# GET SPECIFIC SERVICE TICKET
@service_tickets_bp.route("/<int:service_ticket_id>", methods=["GET"])
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if service_ticket:
        return service_ticket_schema.jsonify(service_ticket), 200
    return jsonify({"error": "Service Ticket not found."}), 404


# GET SERVICE TICKETS BY CUSTOMER
@service_tickets_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(current_customer_id):
    query = select(ServiceTicket).where(
        ServiceTicket.customer_id == current_customer_id
    )

    if not current_customer_id:
        return jsonify({"error": "Customer not found"}), 404
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200


# ADD MECHANIC (singular) TO SERVICE TICKET
@service_tickets_bp.route(
    "/<int:service_ticket_id>/assign-mechanic/<int:mechanic_id>",
    methods=["PUT", "POST"],
)
def add_mechanic_to_service_ticket(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found"}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    # Ensure mechanics relationship is loaded and append if not already present
    if mechanic not in service_ticket.mechanics:
        service_ticket.mechanics.append(mechanic)
        db.session.commit()
        return service_ticket_schema.jsonify(service_ticket), 200
    else:
        return (
            jsonify(
                {
                    "message": f"Mechanic '{mechanic.name}' already assigned to this Service Ticket"
                }
            ),
            200,
        )


# REMOVE MECHANIC (singular) FROM SERVICE TICKET (supports DELETE and PUT)
@service_tickets_bp.route(
    "/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>",
    methods=["DELETE", "PUT"],
)
def remove_mechanic_from_service_ticket(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found"}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    # Ensure mechanics relationship is loaded and remove if present
    if mechanic in service_ticket.mechanics:
        service_ticket.mechanics.remove(mechanic)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Mechanic id: {mechanic_id} '{mechanic.name}' removed from Service Ticket {service_ticket_id}"
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "Mechanic not assigned to this Service Ticket"}), 200


# ADD INVENTORY ITEM (singular) TO SERVICE TICKET
@service_tickets_bp.route(
    "/<int:service_ticket_id>/assign-item/<int:item_id>",
    methods=["PUT", "POST"],
)
def add_item_to_service_ticket(service_ticket_id, item_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found"}), 404

    inventory_item = db.session.get(InventoryItem, item_id)
    if not inventory_item:
        return jsonify({"error": "Inventory Item not found"}), 404

    # Ensure inventory_items relationship is loaded and append if not already present
    if inventory_item not in service_ticket.inventory_items:
        service_ticket.inventory_items.append(inventory_item)
        db.session.commit()
        return service_ticket_schema.jsonify(service_ticket), 200
    else:
        return (
            jsonify(
                {
                    "message": f"Inventory Item '{inventory_item.name}' already exists in this Service Ticket"
                }
            ),
            200,
        )


# REMOVE INVENTORY ITEM (singular) FROM SERVICE TICKET (supports DELETE and PUT)
@service_tickets_bp.route(
    "/<int:service_ticket_id>/remove-item/<int:item_id>",
    methods=["DELETE", "PUT"],
)
def remove_item_from_service_ticket(service_ticket_id, item_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found"}), 404

    inventory_item = db.session.get(InventoryItem, item_id)
    if not inventory_item:
        return jsonify({"error": "Inventory Item not found"}), 404

    # Ensure inventory_items relationship is loaded and remove if present
    if inventory_item in service_ticket.inventory_items:
        service_ticket.inventory_items.remove(inventory_item)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Item id: {inventory_item.id} '{inventory_item.name}' removed from Service Ticket #{service_ticket_id}"
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {
                    "error": f"Item {inventory_item.id} not assigned to this Service Ticket"
                }
            ),
            200,
        )


# DELETE SERVICE TICKET
@service_tickets_bp.route("/<int:service_ticket_id>", methods=["DELETE"])
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found"}), 404

    # Check if any mechanics are still assigned
    if service_ticket.mechanics and len(service_ticket.mechanics) > 0:
        mechanic_ids = [mechanic.id for mechanic in service_ticket.mechanics]
        return (
            jsonify({"error": f"mechanic(s) {mechanic_ids} still assigned to ticket"}),
            400,
        )

    db.session.delete(service_ticket)
    db.session.commit()
    return (
        jsonify(
            {f"message": f"Service Ticket #{service_ticket_id} deleted successfully"}
        ),
        200,
    )


# EDIT SERVICE TICKET (add/remove mechanics)
@service_tickets_bp.route("/<int:service_ticket_id>/edit", methods=["PUT"])
def edit_service_ticket(service_ticket_id):
    try:
        service_ticket_edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    for service_mechanic_id in service_ticket_edits.get("add_mechanic_ids", []):
        query = select(Mechanic).where(Mechanic.id == service_mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    for service_mechanic_id in service_ticket_edits.get("remove_mechanic_ids", []):
        query = select(Mechanic).where(Mechanic.id == service_mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200
