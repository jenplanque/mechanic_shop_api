from xml.parsers.expat import errors
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
    data = request.get_json()

    # Validate input
    try:
        validated_data = service_ticket_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Access model attributes
    customer_id = validated_data.customer_id
    VIN = validated_data.VIN
    service_date = validated_data.service_date
    service_desc = validated_data.service_desc

    # Check for valid customer
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    # Create and save new ticket
    new_ticket = ServiceTicket(
        VIN=VIN,
        service_date=service_date,
        service_desc=service_desc,
        customer_id=customer_id,
    )
    db.session.add(new_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_ticket), 201


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

    result = db.session.execute(query).scalars().all()
    if not result:
        return (
            jsonify({"message": "No open service tickets found for this customer."}),
            200,
        )
    return service_tickets_schema.jsonify(result), 200


# UPDATE SERVICE TICKET - ADD/REMOVE MECHANICS AND INVENTORY
@service_tickets_bp.route("/<int:service_ticket_id>/edit", methods=["PUT"])
def edit_service_ticket(service_ticket_id):
    try:
        service_ticket_edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    if not service_ticket:
        return (
            jsonify(
                {"error": f"Service Ticket #{service_ticket_id} not found in system"}
            ),
            404,
        )

    errors = []

    # Add Mechanics
    for mech_id in service_ticket_edits.get("add_mechanic_ids", []):
        mechanic = db.session.get(Mechanic, mech_id)
        if not mechanic:
            errors.append(f"Mechanic ID '{mech_id}' not found in system")
        elif mechanic in service_ticket.mechanics:
            errors.append(f"Mechanic '{mechanic.name}' already assigned to this ticket")
        else:
            service_ticket.mechanics.append(mechanic)

    # Remove Mechanics
    for mech_id in service_ticket_edits.get("remove_mechanic_ids", []):
        mechanic = db.session.get(Mechanic, mech_id)
        if not mechanic:
            errors.append(f"Mechanic ID '{mech_id}' not found in system")
        elif mechanic not in service_ticket.mechanics:
            errors.append(f"Mechanic '{mechanic.name}' not assigned to this ticket")
        else:
            service_ticket.mechanics.remove(mechanic)

    # Add Inventory Items
    for item_id in service_ticket_edits.get("add_item_ids", []):
        item = db.session.get(InventoryItem, item_id)
        if not item:
            errors.append(f"Inventory item ID '{item_id}' not found in system")
        elif item in service_ticket.inventory_items:
            errors.append(
                f"Inventory item '{item.name}' already assigned to this ticket"
            )
        else:
            service_ticket.inventory_items.append(item)

    # Remove Inventory Items
    for item_id in service_ticket_edits.get("remove_item_ids", []):
        item = db.session.get(InventoryItem, item_id)
        if not item:
            errors.append(f"Inventory item ID '{item_id}' not found in system")
        elif item not in service_ticket.inventory_items:
            errors.append(f"Inventory item '{item.name}' not assigned to this ticket")
        else:
            service_ticket.inventory_items.remove(item)

    db.session.commit()

    return (
        jsonify(
            {
                "message": f"Service Ticket #{service_ticket_id} updated successfully",
                "service_ticket": service_ticket_schema.dump(service_ticket),
                "notes": errors,
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
