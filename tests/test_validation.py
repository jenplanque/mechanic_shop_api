from app import create_app
from app.models import db
import unittest


class TestAPIValidation(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.client = self.app.test_client()

    def test_mechanic_validation(self):
        """Test that mechanic creation returns 400 for missing required fields"""
        # Missing email field
        response = self.client.post(
            "/mechanics/",
            json={"name": "John Doe", "phone": "123-456-7890", "salary": 50000.00},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json)

        # Missing multiple fields should still return 400
        response = self.client.post("/mechanics/", json={"phone": "123-456-7890"})
        self.assertEqual(response.status_code, 400)
        # Should have validation errors for missing required fields
        self.assertTrue(isinstance(response.json, dict))
        self.assertTrue(len(response.json) > 0)

    def test_customer_validation(self):
        """Test that customer creation returns 400 for missing required fields"""
        # Missing email field
        response = self.client.post(
            "/customers/",
            json={
                "name": "Jane Doe",
                "phone": "123-456-7890",
                "password": "password123",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json)

    def test_inventory_validation(self):
        """Test that inventory item creation returns 400 for missing required fields"""
        # Missing name field
        response = self.client.post("/inventory/", json={"price": 29.99})
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.json)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
