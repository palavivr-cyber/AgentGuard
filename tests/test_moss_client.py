import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from src.moss_client import search_moss


class MossClientTests(unittest.TestCase):
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
        self.assertEqual(result["retrieval_mode"], "MOSS")
        self.assertEqual(result["trust"], 0.95)
        self.assertEqual(result["vendor"], "HAL")


if __name__ == "__main__":
    unittest.main()