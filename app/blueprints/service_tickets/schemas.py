from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer_id = fields.Integer(required=True)
    mechanics = fields.Nested("MechanicSchema", only=("id", "name"), many=True)
    customer = fields.Nested("CustomerSchema", only=("id", "name", "email", "phone"))

    class Meta:
        model = ServiceTicket
        fields = (
            "id",
            "VIN",
            "service_date",
            "service_desc",
            "customer_id",
            "customer",
            "mechanics",
        )
        include_fk = True  # Include foreign keys in the schema

    # Explicitly define required fields for better validation
    VIN = fields.String(required=True)
    service_desc = fields.String(required=True)
    service_date = fields.Date(required=True)


class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)

    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()
