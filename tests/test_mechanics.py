from urllib import response
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import create_app
from app.models import db
from flask import current_app
import uuid # is this necessary?


@pytest.fixture
def client():
    app = create_app("TestingConfig")
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()


# HELPER FUNCTION TO CREATE A MECHANIC
def create_test_mechanic():
    return {
        "name": "Jane Wrench",
        "email": "jane@fixit.com",
        "phone": "555-1234",
        "salary": 60000,
    }


# CREATE MECHANIC TESTS
def test_create_mechanic(client):
    response = client.post("/mechanics/", json=create_test_mechanic())
    assert response.status_code == 201
    assert response.json["name"] == "Jane Wrench"


def test_invalid_mechanic_creation(client):
    bad_data = {"name": "Missing Required Fields"}
    response = client.post("/mechanics/", json=bad_data)
    assert response.status_code == 400
    assert "email" in response.json or "Missing" in str(response.json)


def test_create_mechanic_duplicate_email(client):
    client.post("/mechanics/", json=create_test_mechanic())
    response = client.post("/mechanics/", json=create_test_mechanic())
    assert response.status_code == 400
    assert (
        "email already exists" in response.json.get("error", "").lower()
        or "email already exists" in str(response.json).lower()
        or "already exists" in str(response.json).lower()
    )


# GET/SEARCH MECHANIC TESTS
def test_get_all_mechanics(client):
    client.post("/mechanics/", json=create_test_mechanic())
    response = client.get("/mechanics/")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any(m["email"] == "jane@fixit.com" for m in response.json)


def test_get_all_mechanics_empty(client):
    response = client.get("/mechanics/")
    assert response.status_code == 200
    assert response.json == []


def test_get_mechanic_by_id(client):
    res = client.post("/mechanics/", json=create_test_mechanic())
    mechanic_id = res.json["id"]
    response = client.get(f"/mechanics/{mechanic_id}")
    assert response.status_code == 200
    assert response.json["email"] == "jane@fixit.com"


def test_get_mechanic_invalid_id(client):
    response = client.get("/mechanics/9999")
    assert response.status_code == 404
    assert "not found" in response.json.get("error", "").lower()


def test_mechanic_search(client):
    client.post("/mechanics/", json=create_test_mechanic())
    response = client.get("/mechanics/search?name=Jane")
    assert response.status_code == 200
    assert any("Jane" in m["name"] for m in response.json)


def test_mechanic_search_no_results(client):
    response = client.get("/mechanics/search?name=NonExistent")
    assert response.status_code == 404
    assert "No mechanics found with that name" in response.json.get("error", "")


# UPDATE MECHANIC TESTS
def test_update_mechanic(client):
    res = client.post("/mechanics/", json=create_test_mechanic())
    mechanic_id = res.json["id"]
    update_data = {
        "name": "Janet Wrench",
        "email": "jane@fixit.com",
        "phone": "555-5678",
        "salary": 65000,
    }
    response = client.put(f"/mechanics/{mechanic_id}", json=update_data)
    assert response.status_code == 200
    assert response.json["name"] == "Janet Wrench"


def test_update_mechanic_invalid_id(client):
    update_data = {
        "name": "Ghost Mechanic",
        "email": "ghost@nowhere.com",
        "phone": "000-0000",
        "salary": 50000,
    }
    response = client.put("/mechanics/9999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json.get("error", "").lower()


def test_update_mechanic_duplicate_email(client):
    res1 = client.post("/mechanics/", json=create_test_mechanic())
    # Create a second mechanic with a different email to avoid duplicate creation error
    second_mechanic = create_test_mechanic()
    second_mechanic["email"] = "jane2@fixit.com"
    res2 = client.post("/mechanics/", json=second_mechanic)
    mechanic_id = res1.json["id"]
    update_data = {
        "name": "Updated Mechanic",
        "email": res2.json["email"],  # Use the email of the second mechanic
        "phone": "555-9999",
        "salary": 70000,
    }
    response = client.put(f"/mechanics/{mechanic_id}", json=update_data)
    assert response.status_code == 400
    assert "email already exists" in response.json.get("error", "").lower()


# HELPER FUNCTION TO CREATE A TEST CUSTOMER
def create_customer(client):
    customer_data = {
        "name": "Test Customer",
        "email": "customer@test.com",
        "phone": "555-0000",
    }
    response = client.post("/customers/", json=customer_data)
    return response.json["id"], response


# HELPER FUNCTION TO CREATE A TEST TICKET
def create_ticket(customer_id, mechanics=None):
    return {
        "customer_id": customer_id,
        "vehicle": "Test Car",
        "description": "Routine maintenance",
        "mechanics": mechanics or [],
        "status": "open",
    }


# MECHANIC USAGE IN SERVICE TICKETS
def test_mechanic_usage_in_service_tickets(client):
    print("Checking for existing mechanic...")

    # Create mechanic with unique email to avoid duplicate conflict
    unique_email = f"bob_{uuid.uuid4().hex[:6]}@fixit.com"
    mech_res = client.post(
        "/mechanics/",
        json={
            "name": "Tech Bob",
            "email": unique_email,
            "phone": "555-5678",
            "salary": 60000,  # Assuming salary is required
        },
    )
    assert mech_res.status_code == 201
    mechanic_id = mech_res.json["id"]

    # Continue with mechanic usage in service ticket...
    print("Checking for existing customer...")
    # Create customer with full required fields
    cust_res = client.post(
        "/customers/",
        json={
            "name": "Customer Rick",
            "email": "rick@driver.com",
            "phone": "555-1111",
            "password": "pass123",
        },
    )
    print("Customer creation response:", cust_res.status_code, cust_res.json)
    assert cust_res.status_code == 201
    customer_id = cust_res.json["id"]

    # CREATE SERVICE TICKET
    ticket_data = {
        "VIN": "XYZ1234",
        "service_desc": "Brake replacement",
        "service_date": "2025-07-15",
        "customer_id": customer_id,
    }
    ticket_res = client.post("/service_tickets/", json=ticket_data)
    print("Ticket creation response:", ticket_res.status_code, ticket_res.json)
    assert ticket_res.status_code == 201
    ticket_id = ticket_res.json["id"]

    # # EDIT SERVICE TICKET TO ADD MECHANIC
    # update_data = {"add_mechanic_ids": [mechanic_id], "remove_mechanic_ids": []}
    # edit_res = client.put(f"/service_tickets/{ticket_id}/edit", json=update_data)
    # print("Edit response:", edit_res.status_code, edit_res.json)
    # assert edit_res.status_code == 200

    # # Verify mechanic is linked to the service ticket
    # service_ticket = edit_res.json["service_ticket"]
    # mechanic_ids = [m["id"] for m in service_ticket["mechanics"]]
    # assert mechanic_id in mechanic_ids
