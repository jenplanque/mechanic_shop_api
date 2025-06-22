from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested("MechanicSchema", only=("id", "name"), many=True)
    customer = fields.Nested("CustomerSchema", only=("id","name", "email", "phone"))

    class Meta:
        model = ServiceTicket
        fields = (
            "id",
            "VIN",
            "service_date",
            "service_desc",
            "customer",
            "mechanics",
        )
        include_fk = True  # Include foreign keys in the schema

    # You can add custom fields or methods here if needed
    # For example, if you want to include customer name instead of ID:
    # customer_name = fields.Method("get_customer_name")

    # def get_customer_name(self, obj):
    #     return obj.customer.name if obj.customer else None


# class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
#     customer_id = fields.Integer(required=True)

#     class Meta:
#         model = ServiceTicket


class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)

    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()
