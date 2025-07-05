from app.extensions import ma
from app.models import Customer
from marshmallow import fields


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

    # Explicitly define required fields for better validation
    name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)
    password = fields.String(required=True)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(only=("email", "password"))  # For login purposes
