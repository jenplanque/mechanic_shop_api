from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Mechanic
from app.extensions import limiter, cache
from . import mechanics_bp


# ADD MECHANIC
@mechanics_bp.route("/", methods=["POST"])
@cache.cached(timeout=30)  # Cache for 30 seconds to reduce database load
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data["email"])
    existing_mechanic = db.session.execute(query).scalars().all()
    if existing_mechanic:
        return jsonify({"error": "Email already exists"}), 400

    new_mechanic = Mechanic(**mechanic_data)
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


# UPDATE MECHANIC
@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # if new email, verify does not already exist in DB
    if mechanic_data.get("email") != mechanic.email:
        query = select(Mechanic).where(Mechanic.email == mechanic_data["email"])
        existing_mechanic = db.session.execute(query).scalars().first()
        if existing_mechanic:
            return jsonify({"error": "Email already exists"}), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

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


@mechanics_bp.route("/search", methods=["GET"])
def search_mechanics():
    name = request.args.get("name")

    query = select(Mechanic).where(Mechanic.name.like(f'%{name}%'))
    mechanics = db.session.execute(query).scalars().all()
    
    return mechanics_schema.jsonify(mechanics)
