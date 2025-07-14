import pytest
from app import create_app
from app.models import db, Mechanic


@pytest.fixture
def client():
    app = create_app("TestingConfig")
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()


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


# DELETE MECHANIC TESTS
def test_delete_mechanic(client):
    res = client.post("/mechanics/", json=create_test_mechanic())
    mechanic_id = res.json["id"]
    response = client.delete(f"/mechanics/{mechanic_id}")
    assert response.status_code == 200
    assert "deleted" in response.json["message"].lower()


def test_delete_mechanic_invalid_id(client):
    response = client.delete("/mechanics/9999")
    assert response.status_code == 404
    assert "not found" in response.json.get("error", "").lower()
