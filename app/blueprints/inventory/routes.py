from .schemas import inventory_item_schema, inventory_items_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, InventoryItem
from app.extensions import limiter
from . import inventory_items_bp


# ADD INVENTORY ITEM
@inventory_items_bp.route("/", methods=["POST"])
# @cache.cached(timeout=60)  # Cache for 60 seconds to reduce database load
def create_inventory_item():
    try:
        inventory_data = inventory_item_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(InventoryItem).where(InventoryItem.name == inventory_data["name"])
    existing_item = db.session.execute(query).scalars().all()
    if existing_item:
        return jsonify({"error": "Item already exists in Inventory"}), 400

    new_item = InventoryItem(**inventory_data)
    db.session.add(new_item)
    db.session.commit()
    return inventory_item_schema.jsonify(new_item), 201


# GET ALL INVENTORY ITEMS
@inventory_items_bp.route("/", methods=["GET"])
def get_all_inventory_items():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 5))
        query = select(InventoryItem)
        inventory_items = db.paginate(query, page=page, per_page=per_page)
        return inventory_items_schema.jsonify(inventory_items), 200
    except:
        query = select(InventoryItem)
        inventory_items = db.session.execute(query).scalars().all()
        return inventory_items_schema.jsonify(inventory_items), 200


# GET SPECIFIC INVENTORY ITEM
@inventory_items_bp.route("/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    inventory_item = db.session.get(InventoryItem, item_id)

    if inventory_item:
        return inventory_item_schema.jsonify(inventory_item), 200
    return jsonify({"error": "Inventory item not found"}), 404


# UPDATE INVENTORY ITEM
@inventory_items_bp.route("/<int:item_id>", methods=["PUT"])
@limiter.limit(
    "10 per day"
)  # Limit to avoid abuse from excessive changes made to inventory item records
def update_inventory_item(item_id):
    inventory_item = db.session.get(InventoryItem, item_id)

    if not inventory_item:
        return jsonify({"error": "Inventory item not found"}), 404

    try:
        inventory_data = inventory_item_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # if new name, check if item already exists in DB
    if "name" in inventory_data:
        query = select(InventoryItem).where(
            InventoryItem.name == inventory_data["name"],
            InventoryItem.id != item_id,  # Ensure we don't match the current item
        )
        existing_item = db.session.execute(query).scalars().all()
        if existing_item:
            return (
                jsonify({"error": "Item with this name already exists in Inventory"}),
                400,
            )
    for key, value in inventory_data.items():
        setattr(inventory_item, key, value)

    db.session.commit()
    return inventory_item_schema.jsonify(inventory_item), 200


# DELETE INVENTORY ITEM
@inventory_items_bp.route("/<int:item_id>", methods=["DELETE"])
@limiter.limit("5 per day")  # Limit to avoid abuse from excessive deletions
def delete_inventory_item(item_id):
    query = select(InventoryItem).where(InventoryItem.id == item_id)
    inventory_item = db.session.execute(query).scalars().first()

    if not inventory_item:
        return jsonify({"error": "Inventory item not found"}), 404

    db.session.delete(inventory_item)
    db.session.commit()
    return (
        jsonify(
            {
                "message": f"Inventory item id: {item_id}, {inventory_item.name} deleted successfully"
            }
        ),
        200,
    )
