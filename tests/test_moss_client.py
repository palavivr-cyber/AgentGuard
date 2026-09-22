import asyncio
import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from src.moss_client import search_moss
from src.retrieval.moss_client import MossNotConfigured, _get_credentials, moss_configuration


class MossClientTests(unittest.TestCase):
    @patch.dict(os.environ, {"MOSS_ENABLED": "false"}, clear=True)
    def test_explicitly_disabled_moss_does_not_use_credentials(self):
        with self.assertRaises(MossNotConfigured):
            _get_credentials()

    @patch("src.moss_client._get_credentials", return_value=("project-1234", "key"))
    def test_configuration_exposes_non_secret_moss_failure(self, _mock_credentials):
        import src.retrieval.moss_client as moss_client

        previous_reason = moss_client._moss_failure_reason
        moss_client._moss_failure_reason = "ValueError: index does not exist"
        try:
            configuration = moss_configuration()
        finally:
            moss_client._moss_failure_reason = previous_reason

        self.assertEqual(configuration["project_id_suffix"], "1234")
        self.assertEqual(configuration["error"], "ValueError: index does not exist")

    @patch("src.moss_client._get_credentials", return_value=("project", "key"))
    @patch("src.moss_client.MossClient")
    def test_search_maps_official_sdk_result(self, mock_client_class, _mock_credentials):
        mock_client = mock_client_class.return_value
        mock_client.load_index = AsyncMock()
        mock_client.query = AsyncMock(
            return_value=SimpleNamespace(
                docs=[
                    SimpleNamespace(
                        score=0.91,
                        text="Verified invoice context",
                        metadata={
                            "trust": 0.95,
                            "status": "VERIFIED",
                            "vendor": "HAL",
                        },
                    )
                ]
            )
        )

        result = search_moss("a1b2c3d4e5f6g7h8")

        mock_client.load_index.assert_awaited_once_with("agentguard-context")
        mock_client.query.assert_awaited_once()
        query_options = mock_client.query.await_args.args[2]
        self.assertEqual(query_options.filter, {
            "$and": [
                {"field": "doc_hash", "condition": {"$eq": "a1b2c3d4e5f6g7h8"}},
            ],
        })
        self.assertEqual(result["retrieval_mode"], "MOSS")
        self.assertEqual(result["trust"], 0.95)
        self.assertEqual(result["vendor"], "HAL")


if __name__ == "__main__":
    unittest.main()
