import unittest

from fastapi.testclient import TestClient

from agents.msaidizi import route
from api.webhook import app


class SautiYaMwananchiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_about_guardrails(self):
        response = self.client.get("/about")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("Msaidizi", body["agents"])
        self.assertIn("do not store voter ID data", body["guardrails"])

    def test_limuru_routes_to_kiambu(self):
        reply = route("+254700000000", "wapi nipige kura Limuru")
        self.assertIn("LIMURU", reply)
        self.assertIn("KIAMBU", reply)

    def test_kangundo_routes_to_machakos(self):
        reply = route("+254700000000", "wapi nipige kura Kangundo")
        self.assertIn("KANGUNDO", reply)
        self.assertIn("MACHAKOS", reply)

    def test_party_card_claim_false(self):
        reply = route("+254700000000", "Is it true that you need a party card to vote?")
        self.assertIn("Verdict: False", reply)

    def test_unsupported_image_type_is_unverified(self):
        response = self.client.post(
            "/fact-check/image",
            data={"claim_hint": "poster"},
            files={"image": ("poster.gif", b"GIF89a", "image/gif")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Verdict: Unverified", response.json()["reply"])


if __name__ == "__main__":
    unittest.main()
