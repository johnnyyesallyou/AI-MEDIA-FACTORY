import unittest

from fastapi.testclient import TestClient

from main import app


class WorkflowApiTest(unittest.TestCase):
    def test_workflow_catalog_endpoint_is_available(self):
        client = TestClient(app)
        response = client.get('/api/v1/workflows/')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('items', payload)
        self.assertGreaterEqual(len(payload['items']), 1)


if __name__ == '__main__':
    unittest.main()
