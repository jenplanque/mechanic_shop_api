from app.extensions import ma
from app.models import InventoryItem
from marshmallow import fields


class InventoryItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InventoryItem

    # Explicitly define required fields for better validation
    name = fields.String(required=True)
    price = fields.Float(required=True)


inventory_item_schema = InventoryItemSchema()
inventory_items_schema = InventoryItemSchema(many=True)
