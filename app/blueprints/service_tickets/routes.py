from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, ServiceTicket, Customer, Mechanic
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


# ADD MECHANIC TO SERVICE TICKET
@service_tickets_bp.route(
    "/<int:service_ticket_id>/assign-mechanic/<int:mechanic_id>",
    methods=["PUT", "POST"],
)
def add_mechanic_to_service_ticket(service_ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    # Ensure mechanics relationship is loaded and append if not already present
    if mechanic not in service_ticket.mechanics:
        service_ticket.mechanics.append(mechanic)
        db.session.commit()
        return service_ticket_schema.jsonify(service_ticket), 200
    else:
        return (
            jsonify({"message": "Mechanic already assigned to this Service Ticket"}),
            200,
        )


# REMOVE MECHANIC FROM SERVICE TICKET (supports DELETE and PUT)
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
        return jsonify({"error": "Mechanic not on Service Ticket"}), 404

    # Ensure mechanics relationship is loaded and remove if present
    if mechanic in service_ticket.mechanics:
        service_ticket.mechanics.remove(mechanic)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Mechanic {mechanic_id} removed from Service Ticket {service_ticket_id}"
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "Mechanic not assigned to this Service Ticket"}), 200


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
    return jsonify({f"message": f"Service Ticket #{service_ticket_id} deleted successfully"}), 200


@service_tickets_bp.route("/<int:service_ticket_id>", methods=["PUT"])
def edit_service_ticket(service_ticket_id):
    try:
        service_ticket_edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    for service_mechanic_id in service_ticket_edits['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == service_mechanic_id)
        Mechanic = db.session.execute(query).scalars().first()
        
        if Mechanic and Mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(Mechanic)
    
    for service_mechanic_id in service_ticket_edits['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == service_mechanic_id)
        Mechanic = db.session.execute(query).scalars().first()

        if Mechanic and Mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(Mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200
    # return return_loan_schema.jsonify(loan), 200

    # if not service_ticket:
    #     return jsonify({"error": "Service Ticket not found"}), 404

    # for key, value in service_ticket_edits.items():
    #     setattr(service_ticket, key, value)
    # db.session.commit()
    # return service_ticket_schema.jsonify(service_ticket), 200