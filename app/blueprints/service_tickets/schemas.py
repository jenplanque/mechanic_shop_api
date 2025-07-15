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
        )

    mechanics = fields.Nested("MechanicSchema", only=("id", "name"), many=True)
    customer = fields.Nested("CustomerSchema", only=("id", "name", "email", "phone"))


# class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
#     customer_id = fields.Int(required=True)
#     id = fields.Int(dump_only=True)

#     mechanics = fields.Nested("MechanicSchema", only=("id", "name"), many=True)
#     customer = fields.Nested("CustomerSchema", only=("id", "name", "email", "phone"))

#     class Meta:
#         model = ServiceTicket
#         include_fk = True
#         fields = (
#             "id",
#             "VIN",
#             "service_date",
#             "service_desc",
#             "customer_id",
#             "customer",
#             "mechanics",
#         )

#     VIN = fields.Str(required=True)
#     service_desc = fields.Str(required=True)
#     service_date = fields.Date(required=True)


# class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
#     id = fields.Int(dump_only=True)
#     VIN = fields.String(required=True)
#     service_desc = fields.String(required=True)
#     service_date = fields.Date(required=True)
#     customer_id = fields.Integer(required=True)
#     mechanics = fields.Nested("MechanicSchema", only=("id", "name"), many=True)
#     customer = fields.Nested("CustomerSchema", only=("id", "name", "email", "phone"))

#     class Meta:
#         model = ServiceTicket
#         fields = (
#             "id",
#             "VIN",
#             "service_date",
#             "service_desc",
#             "customer_id",
#             "customer",
#             "mechanics",
#         )
#         include_fk = True


class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=False, load_default=[])
    remove_mechanic_ids = fields.List(fields.Int(), required=False, load_default=[])
    add_item_ids = fields.List(fields.Int(), required=False, load_default=[])
    remove_item_ids = fields.List(fields.Int(), required=False, load_default=[])
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids", "add_item_ids", "remove_item_ids")


# class EditServiceTicketSchema(ma.Schema):
#     add_mechanic_ids = fields.List(fields.Int(), required=False, missing=[])
#     remove_mechanic_ids = fields.List(fields.Int(), required=False, missing=[])
#     add_item_ids = fields.List(fields.Int(), required=False, missing=[])
#     remove_item_ids = fields.List(fields.Int(), required=False, missing=[])

#     class Meta:
#         fields = (
#             "add_mechanic_ids",
#             "remove_mechanic_ids",
#             "add_item_ids",
#             "remove_item_ids",
#         )


# class EditServiceTicketSchema(ma.Schema):
#     add_mechanic_ids = fields.List(fields.Int(), required=True)
#     remove_mechanic_ids = fields.List(fields.Int(), required=True)

#     class Meta:
#         fields = ("add_mechanic_ids", "remove_mechanic_ids")


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicketSchema()
