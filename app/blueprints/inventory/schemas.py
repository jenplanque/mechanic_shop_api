from app.extensions import ma
from app.models import InventoryItem
# from marshmallow import fields


class InventoryItemSchema(ma.SQLAlchemyAutoSchema):
    # customer_id = fields.Integer(required=True)
    # mechanics = fields.Nested("MechanicSchema", only=("id", "name"), many=True)
    # customer = fields.Nested("CustomerSchema", only=("id", "name", "email", "phone"))

    class Meta:
        model = InventoryItem
        # fields = (
        #     "id",
        #     "part_name",
        #     "price",
        #     "customer_id",
        #     "customer",
        #     "mechanics",
        # )
        # include_fk = True  # Include foreign keys in the schema


# class EditPartSchema(ma.Schema):
#     add_part_ids = fields.List(fields.Int(), required=True)
#     remove_part_ids = fields.List(fields.Int(), required=True)

#     class Meta:
#         fields = ("add_part_ids", "remove_part_ids")


inventory_item_schema = InventoryItemSchema()
inventory_items_schema = InventoryItemSchema(many=True)
# edit_inventory_item_schema = EditInventoryItemSchema()
