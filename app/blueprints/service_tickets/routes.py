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

        query = select(ServiceTicket).where(ServiceTicket.VIN == service_ticket_data["VIN"])
        existing_service_ticket = db.session.execute(query).scalars().all()
        if existing_service_ticket:
            return jsonify({"error": "Service Ticket with this VIN already exists"}), 400

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


# UPDATE SERVICE TICKET
@service_tickets_bp.route("/<int:service_ticket_id>", methods=["PUT"])
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # if new VIN, verify does not already exist in DB
    if service_ticket_data.get("VIN") != service_ticket.VIN:
        query = select(ServiceTicket).where(ServiceTicket.VIN == service_ticket_data["VIN"])
        existing_service_ticket = db.session.execute(query).scalars().first()
        if existing_service_ticket:
            return jsonify({"error": "Service Ticket with this VIN already exists"}), 400

    for key, value in service_ticket_data.items():
        setattr(service_ticket, key, value)

    db.session.commit()
    return service_ticket_schema.jsonify(service_ticket), 200


# DELETE SERVICE TICKET
@service_tickets_bp.route("/<int:service_ticket_id>", methods=["DELETE"])
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(ServiceTicket, service_ticket_id)

    if not service_ticket:
        return jsonify({"error": "Service Ticket not found."}), 404

    db.session.delete(service_ticket)
    db.session.commit()
    return (
        jsonify({"message": f"Service Ticket id: {service_ticket_id} deleted successfully."}),
        200,
    )
