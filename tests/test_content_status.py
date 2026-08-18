import unittest

from backend.app.api.v1.content import ContentStatus


class ContentStatusApprovalTest(unittest.TestCase):
    def test_approved_status_is_supported(self):
        self.assertIn("approved", ContentStatus.__args__)


if __name__ == "__main__":
    unittest.main()
