"""
Sprint 66.3: Test Automation Manager Endpoints

Tests for automation control endpoints:
- GET /api/v1/automation/ - get settings
- PUT /api/v1/automation/ - update settings
- POST /api/v1/automation/run-now - trigger pipeline
"""

import sys
import os
import unittest

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app


class AutomationManagerTest(unittest.TestCase):
    """Tests for automation management endpoints"""

    def setUp(self):
        """Initialize test client"""
        self.client = TestClient(app)

    def test_automation_config_endpoint_is_available(self):
        """Test GET /api/v1/automation/ returns configuration"""
        response = self.client.get('/api/v1/automation/')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        
        # Verify response structure
        self.assertIn('enabled', payload)
        self.assertIn('research_interval', payload)
        self.assertIn('publish_times', payload)

    def test_automation_config_can_be_updated(self):
        """Test PUT /api/v1/automation/ updates configuration"""
        response = self.client.put(
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
        
        # Verify updated values
        self.assertTrue(payload['enabled'])
        self.assertEqual(payload['research_interval'], '60m')
        self.assertEqual(payload['publish_times'], ['09:00', '13:00', '18:00'])

    def test_run_now_endpoint_is_available(self):
        """Test POST /api/v1/automation/run-now starts pipeline"""
        response = self.client.post('/api/v1/automation/run-now')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        
        # Verify response structure
        self.assertEqual(payload['status'], 'started')
        self.assertIn('execution_id', payload)
        self.assertIn('message', payload)

    def test_scheduler_status_endpoint_is_available(self):
        """Test GET /api/v1/automation/scheduler/status returns scheduler info"""
        response = self.client.get('/api/v1/automation/scheduler/status')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        
        # Verify response structure
        self.assertIn('running', payload)
        self.assertIn('total_jobs', payload)
        self.assertIn('jobs', payload)
        self.assertIsInstance(payload['jobs'], list)


if __name__ == '__main__':
    unittest.main()
