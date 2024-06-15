import unittest

from django.test import Client


class LandingPageTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_landing_page_status_code(self):
        """Test if landing page returns proper status code."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
