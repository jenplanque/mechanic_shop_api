from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer_id = fields.Integer(required=True)
    VIN = fields.String(required=True)
    service_desc = fields.String(required=True)
    service_date = fields.Date(required=True)

    class Meta:
        model = ServiceTicket
        include_fk = True
        load_instance = True
        fields = (
            "id",
            "VIN",
            "service_date",
            "service_desc",
            "customer_id",
            "mechanics",
            "inventory_items",
        )

    mechanics = fields.Nested("MechanicSchema", only=("id", "name"), many=True)
    inventory_items = fields.Nested(
        "InventoryItemSchema", only=("id", "name", "price"), many=True
    )
    customer = fields.Nested("CustomerSchema", only=("id", "name", "email", "phone"))


class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=False, load_default=[])
    remove_mechanic_ids = fields.List(fields.Int(), required=False, load_default=[])
    add_item_ids = fields.List(fields.Int(), required=False, load_default=[])
    remove_item_ids = fields.List(fields.Int(), required=False, load_default=[])

    class Meta:
        fields = (
            "add_mechanic_ids",
            "remove_mechanic_ids",
            "add_item_ids",
            "remove_item_ids",
        )


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()
