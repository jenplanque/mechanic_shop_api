from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer_id = fields.Integer(required=True)

    class Meta:
        model = ServiceTicket


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
