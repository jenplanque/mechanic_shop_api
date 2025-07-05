from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True  # This helps with validation

    # Explicitly define required fields
    name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)
    salary = fields.Float(required=True)


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
