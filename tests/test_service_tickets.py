import pytest
from app import create_app
from app.models import db
import uuid


@pytest.fixture
def client():
    app = create_app("TestingConfig")
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()


# HELPER TO CREATE CUSTOMER
def create_customer(client):
    email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    response = client.post(
        "/customers/",
        json={
            "name": "Test User",
            "email": email,
            "phone": "555-123-4567",
            "password": "securepassword",
        },
    )
    assert response.status_code == 201
    return response.json["id"], email


# HELPER TO CREATE MECHANIC
def create_mechanic(client):
    response = client.post(
        "/mechanics/",
        json={
            "name": "Jane Wrench",
            "email": f"mech_{uuid.uuid4().hex[:6]}@test.com",
            "phone": "555-987-6543",
            "salary": 60000,
        },
    )
    assert response.status_code == 201
    return response.json["id"]


# HELPER TO CREATE INVENTORY ITEM
def create_inventory_item(client):
    response = client.post(
        "/inventory/",
        json={
            "name": "Oil Filter",
            "price": 19.99,
        },
    )
    assert response.status_code == 201
    return response.json["id"]


# HELPER TO CREATE SERVICE TICKET
def create_ticket(customer_id):
    return {
        "VIN": "1HGCM82633A123456",
        "service_desc": "Oil change",
        "service_date": "2025-07-15",
        "customer_id": customer_id,
    }


# ADD SERVICE TICKET
def test_create_ticket(client):
    customer_id, _ = create_customer(client)
    response = client.post("/service_tickets/", json=create_ticket(customer_id))
    assert response.status_code == 201
    assert "id" in response.json


def test_create_ticket_missing_fields(client):
    customer_id, _ = create_customer(client)
    data = create_ticket(customer_id)
    for key in ["VIN", "service_desc", "service_date", "customer_id"]:
        payload = dict(data)
        payload.pop(key)
        res = client.post("/service_tickets/", json=payload)
        assert res.status_code == 400


def test_create_ticket_invalid_customer(client):
    data = create_ticket(9999)  # Invalid ID
    res = client.post("/service_tickets/", json=data)
    assert res.status_code == 404


# GET/SERVICE TICKETS
def test_get_all_tickets_empty(client):
    res = client.get("/service_tickets/")
    assert res.status_code == 200
    assert res.json == []


def test_get_all_tickets(client):
    customer_id, _ = create_customer(client)
    client.post("/service_tickets/", json=create_ticket(customer_id))
    res = client.get("/service_tickets/")
    assert res.status_code == 200
    assert isinstance(res.json, list)


def test_get_ticket_by_id(client):
    customer_id, _ = create_customer(client)
    res = client.post("/service_tickets/", json=create_ticket(customer_id))
    ticket_id = res.json["id"]
    response = client.get(f"/service_tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json["id"] == ticket_id


def test_get_ticket_invalid_id(client):
    res = client.get("/service_tickets/99999")
    assert res.status_code == 404


def test_get_my_tickets_with_token(client):
    customer_id, email = create_customer(client)
    login = client.post(
        "/customers/login", json={"email": email, "password": "securepassword"}
    )
    token = login.json.get("auth_token")
    assert token
    client.post("/service_tickets/", json=create_ticket(customer_id))
    res = client.get(
        "/service_tickets/my-tickets", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert isinstance(res.json, list)


def test_get_my_tickets_no_open_tickets(client):
    _, email = create_customer(client)
    login = client.post(
        "/customers/login", json={"email": email, "password": "securepassword"}
    )
    token = login.json.get("auth_token")
    assert token
    res = client.get(
        "/service_tickets/my-tickets", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json["message"] == "No open service tickets found for this customer."


def test_get_my_tickets_invalid_token(client):
    response = client.get(
        "/service_tickets/my-tickets", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "invalid" in response.json.get("message", "").lower()


# UPDATE SERVICE TICKET (add/remove mechanics)
def test_update_ticket_mechanics(client):
    customer_id, _ = create_customer(client)
    ticket_data = create_ticket(customer_id)
    res = client.post("/service_tickets/", json=ticket_data)
    ticket_id = res.json["id"]

    mechanic_id = create_mechanic(client)

    update_data = {"add_mechanic_ids": [mechanic_id], "remove_mechanic_ids": []}
    update_res = client.put(f"/service_tickets/{ticket_id}/edit", json=update_data)
    assert update_res.status_code == 200
    assert mechanic_id in [
        m["id"] for m in update_res.json["service_ticket"]["mechanics"]
    ]


def test_update_ticket_mechanics_invalid_ticket(client):
    mechanic_id = create_mechanic(client)
    update_data = {"add_mechanic_ids": [mechanic_id], "remove_mechanic_ids": []}
    res = client.put("/service_tickets/9999/edit", json=update_data)
    assert res.status_code == 404
    assert "not found" in res.json.get("error", "").lower()


def test_update_ticket_mechanics_invalid_mechanic(client):
    customer_id, _ = create_customer(client)
    ticket_data = create_ticket(customer_id)
    res = client.post("/service_tickets/", json=ticket_data)
    ticket_id = res.json["id"]

    update_data = {
        "add_mechanic_ids": [9999],  # Invalid mechanic ID
        "remove_mechanic_ids": [],
    }
    res = client.put(f"/service_tickets/{ticket_id}/edit", json=update_data)
    assert res.status_code == 404
    assert "not found" in res.json.get("error", "").lower()


# UPDATE SERVICE TICKET (add/remove inventory items)
def test_update_ticket_inventory(client):
    customer_id, _ = create_customer(client)
    ticket_data = create_ticket(customer_id)
    res = client.post("/service_tickets/", json=ticket_data)
    ticket_id = res.json["id"]

    item_id = create_inventory_item(client)


    update_data = {"add_item_ids": [item_id], "remove_item_ids": []}
    update_res = client.put(f"/service_tickets/{ticket_id}/edit", json=update_data)
    assert update_res.status_code == 200
    assert item_id in [
        i["id"] for i in update_res.json["service_ticket"]["inventory_items"]
    ]


# DELETE SERVICE TICKET
def test_delete_ticket(client):
    customer_id, _ = create_customer(client)
    res = client.post("/service_tickets/", json=create_ticket(customer_id))
    ticket_id = res.json["id"]
    del_res = client.delete(f"/service_tickets/{ticket_id}")
    assert del_res.status_code == 200
    assert "deleted" in del_res.json["message"].lower()


def test_delete_ticket_not_found(client):
    res = client.delete("/service_tickets/9999")
    assert res.status_code == 404
