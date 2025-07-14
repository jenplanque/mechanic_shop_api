from urllib import response
import pytest
from app import create_app
from app.models import db, Customer
from flask import current_app


@pytest.fixture
def client():
    app = create_app("TestingConfig")
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()


# HELPER FUNCTION TO CREATE A CUSTOMER
def create_test_customer():
    return {
        "name": "John Doe",
        "email": "jd@customer.com",
        "phone": "123-456-7890",
        "password": "securepassword",
    }


# def create_customer(client):
#     response = client.post(
#         "/customers/",
#         json={
#             "name": "Jane Doe",
#             "email": "jane@customer.com",
#             "phone": "503-555-5678",
#             "password": "securepassword",
#         },
#     )
#     return response.json["id"]


# # HELPER FUNCTION TO CREATE A SERVICE TICKET
# def create_ticket(customer_id):
#     return {
#         "VIN": "ABC123XYZ",
#         "service_desc": "Oil change and tire rotation",
#         "service_date": "2025-07-13",
#         "customer_id": customer_id,
#         "customer": {
#             "id": customer_id,
#             "name": "Jane Doe",
#             "email": "jane@customer.com",
#             "phone": "503-555-5678",
#         },
#     }


# CREATE CUSTOMER TESTS
def test_create_customer(client):
    response = client.post("/customers/", json=create_test_customer())
    assert response.status_code == 201
    assert response.json["name"] == "John Doe"


def test_invalid_customer_creation(client):
    bad_data = {"name": "No Email", "password": "123"}
    response = client.post("/customers/", json=bad_data)
    assert response.status_code == 400
    assert "email" in response.json

def test_create_customer_duplicate_email(client):
    client.post("/customers/", json=create_test_customer())
    response = client.post("/customers/", json=create_test_customer())
    assert response.status_code == 400
    assert (
        "email already exists" in response.json.get("error", "").lower()
        or "already exists" in str(response.json).lower()
    )


# CUSTOMER LOGIN TESTS
def test_customer_login_success(client):
    client.post("/customers/", json=create_test_customer())
    credentials = {"email": "jd@customer.com", "password": "securepassword"}
    response = client.post("/customers/login", json=credentials)
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert "auth_token" in response.json


def test_customer_login_failure(client):
    credentials = {"email": "wrong@customer.com", "password": "badpass"}
    response = client.post("/customers/login", json=credentials)
    assert response.status_code == 401
    # assert response.json["message"] == "Invalid email or password!"
    assert "invalid" in response.json.get("error", "").lower()


# GET/SEARCH CUSTOMER TESTS
def test_get_all_customers(client):
    client.post("/customers/", json=create_test_customer())
    response = client.get("/customers/")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any(c["email"] == "jd@customer.com" for c in response.json)

def test_get_all_customers_empty(client):
    response = client.get("/customers/")
    assert response.status_code == 200
    assert response.json == []


# def test_get_tickets_by_customer_id(client):
#     customer_id = create_customer(client)
#     client.post("/service_tickets/", json=create_ticket(customer_id))
#     response = client.get(f"/customers/{customer_id}/tickets")
#     assert response.status_code == 200
#     assert isinstance(response.json, list)
#     assert all(ticket["customer_id"] == customer_id for ticket in response.json)

# def test_get_tickets_by_invalid_customer_id(client):
#     response = client.get("/customers/9999/tickets")
#     assert response.status_code == 404
#     assert "not found" in response.json.get("error", "").lower()


# UPDATE CUSTOMER TESTS
def test_update_customer(client):
    client.post("/customers/", json=create_test_customer())
    login_res = client.post(
        "/customers/login",
        json={"email": "jd@customer.com", "password": "securepassword"},
    )
    token = login_res.json["auth_token"]

    update_payload = {
        "name": "John Updated",
        "phone": "999-999-9999",
        "email": "jd@customer.com",
        "password": "securepassword",
    }

    response = client.put(
        "/customers/", json=update_payload, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json["name"] == "John Updated"

def test_update_customer_invalid_token(client):
    client.post("/customers/", json=create_test_customer())
    update_payload = {
        "name": "John Updated",
        "phone": "999-999-9999",
        "email": "jd@customer.com",
        "password": "securepassword",
    }

    response = client.put(
        "/customers/", json=update_payload, headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "invalid" in response.json.get("message", "").lower()


# DELETE CUSTOMER TESTS
def test_delete_customer(client):
    # Create the customer
    res = client.post("/customers/", json=create_test_customer())
    assert res.status_code == 201

    # Log them in
    login_res = client.post(
        "/customers/login",
        json={"email": "jd@customer.com", "password": "securepassword"},
    )
    token = login_res.json["auth_token"]

    # Send DELETE request (no ID in URL!)
    response = client.delete(
        "/customers/", headers={"Authorization": f"Bearer {token}"}  # ✅ corrected URL
    )
    print("DELETE /customers/ response:", response.status_code, response.json)
    assert response.status_code == 200
    assert "deleted" in response.json["message"].lower()

def test_delete_customer_invalid_token(client):
    # Create the customer
    client.post("/customers/", json=create_test_customer())

    # Send DELETE request with invalid token
    response = client.delete(
        "/customers/", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "invalid" in response.json.get("message", "").lower()
