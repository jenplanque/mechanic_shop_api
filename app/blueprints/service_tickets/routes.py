from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, ServiceTicket, Customer, Mechanic

from . import service_tickets_bp


# ADD SERVICE TICKET and GET ALL SERVICE TICKETS
@service_tickets_bp.route("/", methods=["POST", "GET"])
def service_tickets():
    if request.method == "POST":
        try:
            service_ticket_data = service_ticket_schema.load(request.json)

        except ValidationError as e:
            return jsonify(e.messages), 400

        query = select(ServiceTicket).where(
            ServiceTicket.VIN == service_ticket_data["VIN"]
        )
        existing_service_ticket = db.session.execute(query).scalars().all()
        if existing_service_ticket:
            return (
                jsonify({"error": "Service Ticket with this VIN already exists"}),
                400,
            )

        # Verify that the customer_id exists in the Customer table before proceeding
        customer_id = service_ticket_data.get("customer_id")
        if not customer_id or not db.session.get(Customer, customer_id):
            return jsonify({"error": "Customer not found."}), 404

        new_service_ticket = ServiceTicket(**service_ticket_data)
        db.session.add(new_service_ticket)
        db.session.commit()
        return service_ticket_schema.jsonify(new_service_ticket), 201

    elif request.method == "GET":
        query = select(ServiceTicket)
        service_tickets = db.session.execute(query).scalars().all()

        return service_tickets_schema.jsonify(service_tickets), 200


# GET SPECIFIC SERVICE TICKET
@service_tickets_bp.route("/<int:service_ticket_id>", methods=["GET"])
def get_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if service_ticket:
        return service_ticket_schema.jsonify(service_ticket), 200
    return jsonify({"error": "Service Ticket not found."}), 404


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
    return jsonify({"message": "Service Ticket deleted successfully"}), 200
