import unittest

from src.execution_service import execute_tool
from src.review import REVIEW_QUEUE
from src.review_service import create_pending_review, get_review


class ExecutionReviewTests(unittest.TestCase):
    def setUp(self):
        REVIEW_QUEUE.clear()

    def test_only_allow_executes(self):
        allowed = execute_tool("payment", "REQ-1", {"decision": "ALLOW"})
        blocked = execute_tool("payment", "REQ-2", {"decision": "BLOCK"})
        review = execute_tool("payment", "REQ-3", {"decision": "REVIEW"})

        self.assertTrue(allowed.executed)
        self.assertFalse(blocked.executed)
        self.assertFalse(review.executed)

    def test_review_can_be_retrieved(self):
        request = create_pending_review(
            "read_email",
            "doc-1",
            {
                "decision": "REVIEW",
                "reason": "Needs review",
                "reason_code": "REVIEW_REQUIRED",
                "policy_version": "agentguard-default-v1",
                "trust": 0.82,
            },
        )

        self.assertEqual(get_review(request["review_id"]), request)
        self.assertEqual(request["status"], "PENDING")


if __name__ == "__main__":
    unittest.main()