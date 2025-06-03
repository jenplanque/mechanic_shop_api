from datetime import date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List
from marshmallow import ValidationError
from sqlalchemy import select
import os
from dotenv import load_dotenv

load_dotenv()

# app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     f"mysql+mysqlconnector://root:{os.getenv('DB_PW')}@localhost/mechanic_db"
# )


# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Create a base class for our models

# -------SCHEMAS-------#
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        # load_instance = True


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


# ------ROUTES-------#


# ADD CUSTOMER and GET ALL CUSTOMERS
@app.route("/customers", methods=["POST", "GET"])
def customers():
    if request.method == "POST":
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

    elif request.method == "GET":
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()

        return customers_schema.jsonify(customers), 200


# GET SPECIFIC CUSTOMER
@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404


# UPDATE CUSTOMER
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

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
@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return (
        jsonify({"message": f"Customer id: {customer_id} deleted successfully."}),
        200,
    )


# use below to test the connection
# @app.route("/members", methods=["GET"])
# def get_members():
#     return {"message": "Members endpoint is working!"}


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run()
