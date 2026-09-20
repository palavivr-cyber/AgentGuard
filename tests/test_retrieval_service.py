import unittest
from unittest.mock import patch

from src.retrieval_service import retrieve_context


class RetrievalServiceTests(unittest.TestCase):
    def test_local_demo_trusted_context_is_normalized(self):
        result = retrieve_context("a1b2c3d4e5f6g7h8")

        self.assertEqual(result.retrieval_mode, "LOCAL_DEMO")
        self.assertEqual(result.trust, 0.95)
        self.assertGreaterEqual(result.latency, 0.0)

    @patch("src.retrieval_service.search_moss")
    def test_moss_success_is_returned_as_moss(self, mock_search):
        mock_search.return_value = {
            "found": True,
            "trust": 0.94,
            "latency": 3.1,
            "doc": "Moss invoice match",
            "status": "VERIFIED",
            "vendor": "HAL",
            "retrieval_mode": "MOSS",
        }

        result = retrieve_context("external-doc-id")

        self.assertEqual(result.retrieval_mode, "MOSS")
        self.assertEqual(result.trust, 0.94)

    @patch("src.retrieval_service.search_moss")
    def test_provider_failure_is_fail_closed(self, mock_search):
        mock_search.side_effect = RuntimeError("provider unavailable")

        result = retrieve_context("external-doc-id")

        self.assertEqual(result.retrieval_mode, "MOSS_ERROR")
        self.assertEqual(result.trust, 0.0)

    @patch("src.retrieval_service.search_moss")
    def test_malformed_provider_data_is_normalized(self, mock_search):
        mock_search.return_value = {
            "trust": "invalid",
            "latency": -4,
            "retrieval_mode": "MOSS",
        }

        result = retrieve_context("external-doc-id")

        self.assertEqual(result.trust, 0.0)
        self.assertEqual(result.latency, 0.0)
        self.assertEqual(result.retrieval_mode, "MOSS")


if __name__ == "__main__":
    unittest.main()
