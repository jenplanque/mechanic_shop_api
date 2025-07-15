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

    # if not current_customer_id:
    #     return jsonify({"error": "Customer not found"}), 404
    result = db.session.execute(query).scalars().all()
    if not result:
        return (
            jsonify({"message": "No open service tickets found for this customer."}),
            200,
        )
    return service_tickets_schema.jsonify(result), 200


# EDIT SERVICE TICKET (add/remove mechanics)
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

    # Add mechanics
    for mech_id in service_ticket_edits.get("add_mechanic_ids", []):
        mechanic = db.session.get(Mechanic, mech_id)
        if not mechanic:
            return jsonify({"error": f"Mechanic: '{mech_id}' not found in system"}), 404
        if mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    # Remove mechanics
    for mech_id in service_ticket_edits.get("remove_mechanic_ids", []):
        mechanic = db.session.get(Mechanic, mech_id)
        if not mechanic:
            return jsonify({"error": f"Mechanic: '{mech_id}' not found in system"}), 404
        if mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    # Add inventory items
    for item_id in service_ticket_edits.get("add_item_ids", []):
        item = db.session.get(InventoryItem, item_id)
    if item is None:
        errors.append(f"Inventory item ID '{item_id}' not found in system")
        # item = db.session.get(InventoryItem, item_id)
    # if not item:
        # errors.append(f"Inventory item ID '{item_id}' not found in system")
    elif item not in service_ticket.inventory_items:
        service_ticket.inventory_items.append(item)
    else:
        errors.append(f"Inventory item ID '{item_id}' already assigned to this ticket")
    # for item_id in service_ticket_edits.get("add_item_ids", []):
    #     item = db.session.get(InventoryItem, item_id)
    #     if not item:
    #         return (
    #             jsonify({"error": f"Inventory item: '{item_id}' not found in system"}),
    #             404,
    #         )
        if item not in service_ticket.inventory_items:
            service_ticket.inventory_items.append(item)

    # Remove inventory items
    for item_id in service_ticket_edits.get("remove_item_ids", []):
        item = db.session.get(InventoryItem, item_id)
        if not item:
            errors.append(f"Inventory item ID '{item_id}' not found in system")
        elif item in service_ticket.inventory_items:
            service_ticket.inventory_items.remove(item)
        else:
            errors.append(f"Inventory item ID '{item_id}' not assigned to this ticket")
    
    # for item_id in service_ticket_edits.get("remove_item_ids", []):
    #     item = db.session.get(InventoryItem, item_id)
    #     if not item:
    #         return (
    #             jsonify({"error": f"Inventory item: '{item_id}' not found in system"}),
    #             404,
    #         )
        if item in service_ticket.inventory_items:
            service_ticket.inventory_items.remove(item)

    db.session.commit()
    return (
        jsonify(
            {
                "message": f"Service Ticket #{service_ticket_id} updated successfully",
                "service_ticket": {
                    "id": service_ticket.id,
                    "description": service_ticket.description,
                    "mechanics": [mechanic.id for mechanic in service_ticket.mechanics],
                    "inventory_items": [item.to_dict() for item in service_ticket.inventory_items]
                }
                # "service_ticket": service_ticket_schema.dump(service_ticket),
            }
        ),
        200,
    )


# @service_tickets_bp.route("/<int:service_ticket_id>/edit", methods=["PUT"])
# def edit_service_ticket(service_ticket_id):
#     try:
#         service_ticket_edits = edit_service_ticket_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400

#     query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
#     service_ticket = db.session.execute(query).scalars().first()

#     for service_mechanic_id in service_ticket_edits.get("add_mechanic_ids", []):
#         query = select(Mechanic).where(Mechanic.id == service_mechanic_id)
#         mechanic = db.session.execute(query).scalars().first()

#         if not service_ticket:
#             return (
#                 jsonify(
#                     {
#                         "error": f"Service Ticket #{service_ticket_id} not found in system"
#                     }
#                 ),
#                 404,
#             )
#         if not mechanic:
#             return (
#                 jsonify(
#                     {"error": f"Mechanic: '{service_mechanic_id}' not found in system"}
#                 ),
#                 404,
#             )

#         if mechanic and mechanic in service_ticket.mechanics:
#             return (
#                 jsonify(
#                     {
#                         "error": f"Mechanic: '{mechanic.name}' already assigned to Service Ticket #{service_ticket_id}"
#                     }
#                 ),
#                 400,
#             )
#         if mechanic and mechanic not in service_ticket.mechanics:
#             service_ticket.mechanics.append(mechanic)

#     for service_mechanic_id in service_ticket_edits.get("remove_mechanic_ids", []):
#         query = select(Mechanic).where(Mechanic.id == service_mechanic_id)
#         mechanic = db.session.execute(query).scalars().first()

#         if not service_ticket:
#             return (
#                 jsonify(
#                     {
#                         "error": f"Service Ticket #{service_ticket_id} not found in system"
#                     }
#                 ),
#                 404,
#             )
#         if not mechanic:
#             return (
#                 jsonify(
#                     {"error": f"Mechanic: '{service_mechanic_id}' not found in system"}
#                 ),
#                 404,
#             )

#         if mechanic and mechanic not in service_ticket.mechanics:
#             return (
#                 jsonify(
#                     {
#                         "error": f"Mechanic: '{mechanic.name}' not assigned to Service Ticket #{service_ticket_id}"
#                     }
#                 ),
#                 400,
#             )
#         if mechanic and mechanic in service_ticket.mechanics:
#             service_ticket.mechanics.remove(mechanic)

#     db.session.commit()
#     return (
#         jsonify(
#             {
#                 "message": f"Service Ticket #{service_ticket_id} updated successfully",
#                 "service_ticket": service_ticket_schema.dump(service_ticket),
#             }
#         ),
#         200,
#     )


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
        return (
            jsonify(
                {
                    "message": f"'{inventory_item.name}' successfully added to Ticket #{service_ticket_id}"
                }
            ),
            200,
        )
    else:
        return (
            jsonify({"message": f"'{inventory_item.name}' already assigned to Ticket"}),
            400,
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
                    "message": f"'{inventory_item.name}' removed from Service Ticket #{service_ticket_id}"
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {
                    "error": f"Item id: {inventory_item.id} not assigned to this Service Ticket"
                }
            ),
            400,
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
