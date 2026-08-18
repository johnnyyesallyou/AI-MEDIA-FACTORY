import unittest

from fastapi.testclient import TestClient

from main import app


class AutomationManagerTest(unittest.TestCase):
    def test_automation_config_endpoint_is_available(self):
        client = TestClient(app)
        response = client.get('/api/v1/automation/')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('enabled', payload)
        self.assertIn('research_interval', payload)
        self.assertIn('publish_times', payload)

    def test_automation_config_can_be_updated(self):
        client = TestClient(app)
        response = client.put(
            '/api/v1/automation/',
            json={
                'enabled': True,
                'research_interval': '60m',
                'publish_times': ['09:00', '13:00', '18:00'],
                'timezone': 'Europe/Moscow',
                'auto_publish': False,
                'human_review': True,
                'max_posts_per_day': 5,
                'breaking_news': True,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['enabled'])
        self.assertEqual(payload['research_interval'], '60m')
        self.assertEqual(payload['publish_times'], ['09:00', '13:00', '18:00'])

    def test_run_now_endpoint_is_available(self):
        client = TestClient(app)
        response = client.post('/api/v1/automation/run-now')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['status'], 'started')


if __name__ == '__main__':
    unittest.main()
