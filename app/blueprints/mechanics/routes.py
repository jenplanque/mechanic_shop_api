from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Mechanic
from app.extensions import limiter, cache
from . import mechanics_bp


# ADD MECHANIC
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    print("Checking for existing mechanic...")
    data = request.json

    # Check for duplicate email FIRST
    existing_query = select(Mechanic).where(Mechanic.email == data.get("email"))
    existing_mechanic = db.session.execute(existing_query).scalars().first()
    if existing_mechanic:
        print("Duplicate found:", existing_mechanic.email)
        return jsonify({"error": "Email already exists"}), 400

    # Then load and validate the new mechanic
    try:
        new_mechanic = mechanic_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


# GET ALL MECHANICS
@mechanics_bp.route("/", methods=["GET"])
@limiter.limit("5 per minute")  # Limit to avoid abuse from excessive requests
def get_all_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics), 200


# GET SPECIFIC MECHANIC
@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    return jsonify({"error": "Mechanic not found."}), 404


# SEARCH MECHANICS BY NAME
@mechanics_bp.route("/search", methods=["GET"])
def search_mechanics():
    name = request.args.get("name")

    query = select(Mechanic).where(Mechanic.name.like(f"%{name}%"))
    mechanics = db.session.execute(query).scalars().all()

    if not mechanics:
        return jsonify({"error": "No mechanics found with that name."}), 404
    return mechanics_schema.jsonify(mechanics)


# UPDATE MECHANIC
@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        updated_mechanic = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # if new email, verify does not already exist in DB
    if updated_mechanic.email != mechanic.email:
        query = select(Mechanic).where(Mechanic.email == updated_mechanic.email)
        existing_mechanic = db.session.execute(query).scalars().first()
        if existing_mechanic:
            return jsonify({"error": "Email already exists"}), 400

    # Update the existing mechanic with new values
    mechanic.name = updated_mechanic.name
    mechanic.email = updated_mechanic.email
    mechanic.phone = updated_mechanic.phone
    mechanic.salary = updated_mechanic.salary

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# DELETE MECHANIC
@mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
@limiter.limit("5 per day")  # Limit to avoid abuse from excessive deletions
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return (
        jsonify({"message": f"Mechanic id: {mechanic_id} deleted successfully."}),
        200,
    )


# MECHANIC USAGE
@mechanics_bp.route("/usage", methods=["GET"])
def mechanic_usage():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)

    return (
        jsonify(
            [
                {
                    "id": mechanic.id,
                    "name": mechanic.name,
                    "ticket_count": len(mechanic.service_tickets),
                }
                for mechanic in mechanics
            ]
        ),
        200,
    )
