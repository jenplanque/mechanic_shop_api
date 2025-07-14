from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Customer
from app.extensions import limiter, cache
from . import customers_bp
from app.utils.util import encode_token, token_required


# CUSTOMER LOGIN
@customers_bp.route("/login", methods=["POST"])
def login_customer():
    try:
        credentials = login_schema.load(request.json)
        email = credentials["email"]
        password = credentials["password"]
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == email)
    customer = (
        db.session.execute(query).scalars().first()
    )  # query cust table for cust with this email

    if customer and customer.password == password:
        auth_token = encode_token(customer.id)  # Encode the token with customer ID

        response = {
            "status": "success",
            "message": "Login successful",
            "auth_token": auth_token,
        }
        return jsonify(response), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


# ADD CUSTOMER
@customers_bp.route("/", methods=["POST"])
def create_customer():
    print("Checking for existing customer...")
    try:
        customer_data = customer_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data["email"])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already exists"}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


# GET ALL CUSTOMERS
@customers_bp.route("/", methods=["GET"])
def get_all_customers():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 5))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(customers), 200


# UPDATE CUSTOMER
@customers_bp.route("/", methods=["PUT"])
@token_required  # Ensure the user is authenticated before allowing updates
@limiter.limit(
    "10 per day"
)  # Limit to avoid abuse from excessive changes made to customer records
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # if new email, verify does not already exist in DB
    if customer_data.get("email") != customer.email:
        query = select(Customer).where(Customer.email == customer_data["email"])
        existing_customer = db.session.execute(query).scalars().first()
        if existing_customer:
            return jsonify({"error": "Email already exists"}), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# DELETE CUSTOMER
@customers_bp.route("/", methods=["DELETE"])
@token_required  # Ensure the user is authenticated before allowing deletion
@limiter.limit("5 per day")  # Limit to avoid abuse from excessive deletions
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()
    return (
        jsonify({"message": f"Customer id: {customer_id} deleted successfully"}),
        200,
    )
