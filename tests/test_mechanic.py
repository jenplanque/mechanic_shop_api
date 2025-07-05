from app import create_app
from app.models import db
import unittest


class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.client = self.app.test_client()

    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "123-456-7890",
            "salary": 50000.00,
        }

        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "John Doe")


    def test_invalid_creation(self):
        mechanic_payload = {
            "name": "John Doe",
            "phone": "123-456-7890",
            "salary": 50000.00,
        }
        print("Payload being sent:", mechanic_payload)
        response = self.client.post("/mechanics/", json=mechanic_payload)
        print("Response status code:", response.status_code)
        print("Response JSON:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["email"], ["Missing data for required field."])


    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
