import pytest
from app import create_app
from app.models import db


@pytest.fixture
def client():
    app = create_app("TestingConfig")
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()


def create_test_part():
    return {
        "name": "Brake Pads",
        "price": 49.99,
    }


# CREATE INVENTORY ITEM TESTS
def test_create_inventory_item(client):
    response = client.post("/inventory/", json=create_test_part())
    assert response.status_code == 201
    assert response.json["name"] == "Brake Pads"


def test_invalid_inventory_creation(client):
    bad_data = {"price": 12.99}
    response = client.post("/inventory/", json=bad_data)
    assert response.status_code == 400
    assert "name" in str(response.json)
    
def test_create_inventory_duplicate_name(client):
    client.post("/inventory/", json=create_test_part())
    response = client.post("/inventory/", json=create_test_part())
    assert response.status_code == 400
    assert "already exists" in str(response.json).lower() or "item already exists" in str(response.json).lower()


# GET/SEARCH INVENTORY ITEM TESTS
def test_get_all_inventory(client):
    client.post("/inventory/", json=create_test_part())
    response = client.get("/inventory/")
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert any(p["name"] == "Brake Pads" for p in response.json)


def test_get_all_inventory_empty(client):
    response = client.get("/inventory/")
    assert response.status_code == 200
    assert response.json == []


def test_get_inventory_by_id(client):
    res = client.post("/inventory/", json=create_test_part())
    part_id = res.json["id"]
    response = client.get(f"/inventory/{part_id}")
    assert response.status_code == 200
    assert response.json["name"] == "Brake Pads"


def test_get_inventory_invalid_id(client):
    response = client.get("/inventory/9999")
    assert response.status_code == 404
    assert "not found" in str(response.json).lower()


# UPDATE INVENTORY ITEM TESTS
def test_update_inventory(client):
    res = client.post("/inventory/", json=create_test_part())
    part_id = res.json["id"]
    update_data = {
        "name": "Brake Pads - Premium",
        "price": 59.99,
    }
    response = client.put(f"/inventory/{part_id}", json=update_data)
    assert response.status_code == 200
    assert response.json["name"] == "Brake Pads - Premium"


def test_update_inventory_invalid_id(client):
    update_data = {"name": "Invalid Part", "price": 0.0}
    response = client.put("/inventory/9999", json=update_data)
    assert response.status_code == 404
    assert "not found" in str(response.json).lower()


def test_update_inventory_duplicate_name(client):
    part1 = {"name": "Brake Pads", "price": 49.99}
    part2 = {"name": "Oil Filter", "price": 19.99}
    client.post("/inventory/", json=part1)
    res2 = client.post("/inventory/", json=part2)
    id2 = res2.json["id"]
    update_data = {"name": "Brake Pads", "price": 19.99}
    response = client.put(f"/inventory/{id2}", json=update_data)
    assert response.status_code == 400
    assert "already exists" in str(response.json).lower()


# DELETE INVENTORY ITEM TESTS
def test_delete_inventory(client):
    res = client.post("/inventory/", json=create_test_part())
    part_id = res.json["id"]
    response = client.delete(f"/inventory/{part_id}")
    assert response.status_code == 200
    assert "deleted" in response.json["message"].lower()


def test_delete_inventory_invalid_id(client):
    response = client.delete("/inventory/9999")
    assert response.status_code == 404
    assert "not found" in str(response.json).lower()


# PAGINATION
def test_get_inventory_with_pagination(client):
    for i in range(3):
        client.post("/inventory/", json={"name": f"Part {i}", "price": 10.0 + i})
    response = client.get("/inventory/?page=1")
    assert response.status_code == 200
    assert isinstance(response.json, list)
