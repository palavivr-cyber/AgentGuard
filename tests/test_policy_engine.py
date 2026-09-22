import unittest

from src.policy_engine import evaluate_policy
from src.retrieval_models import RetrievalResult


def context(trust=0.95, found=True, status="VERIFIED", retrieval_mode="LOCAL_DEMO"):
    return RetrievalResult(
        found=found,
        trust=trust,
        latency=1.0,
        doc="Test context" if found else "UNKNOWN",
        status=status,
        vendor="TestVendor",
        retrieval_mode=retrieval_mode,
    )


class PolicyEngineTests(unittest.TestCase):
    def test_trusted_context_allows(self):
        result = evaluate_policy("payment", context())

        self.assertEqual(result.decision, "ALLOW")
        self.assertEqual(result.reason_code, "CONTEXT_ACCEPTED")
        self.assertEqual(result.policy_version, "agentguard-default-v1")

    def test_low_trust_blocks(self):
        result = evaluate_policy("read_email", context(trust=0.69))

        self.assertEqual(result.decision, "BLOCK")
        self.assertEqual(result.reason_code, "LOW_TRUST")

    def test_payment_requires_high_risk_threshold(self):
        result = evaluate_policy("payment", context(trust=0.89))

        self.assertEqual(result.decision, "BLOCK")
        self.assertEqual(result.reason_code, "HIGH_RISK_THRESHOLD")

    def test_medium_trust_requires_review(self):
        result = evaluate_policy("read_email", context(trust=0.82))

        self.assertEqual(result.decision, "REVIEW")
        self.assertEqual(result.reason_code, "REVIEW_REQUIRED")

    def test_explicit_review_status_requires_human_review(self):
        result = evaluate_policy("read_email", context(trust=0.82, status="REVIEW"))

        self.assertEqual(result.decision, "REVIEW")
        self.assertEqual(result.reason_code, "REVIEW_REQUIRED")

    def test_explicit_review_status_blocks_payment(self):
        result = evaluate_policy("payment", context(trust=0.82, status="REVIEW"))

        self.assertEqual(result.decision, "BLOCK")
        self.assertEqual(result.reason_code, "HIGH_RISK_REVIEW_REQUIRED")

    def test_threshold_boundaries(self):
        self.assertEqual(evaluate_policy("read_email", context(trust=0.70)).decision, "REVIEW")
        self.assertEqual(evaluate_policy("read_email", context(trust=0.85)).decision, "ALLOW")
        self.assertEqual(evaluate_policy("payment", context(trust=0.90)).decision, "ALLOW")

    def test_missing_context_blocks(self):
        result = evaluate_policy("payment", context(found=False))

        self.assertEqual(result.decision, "BLOCK")
        self.assertEqual(result.reason_code, "CONTEXT_NOT_FOUND")

    def test_retrieval_failure_blocks(self):
        result = evaluate_policy("payment", context(found=False, trust=0.0, retrieval_mode="MOSS_ERROR"))

        self.assertEqual(result.decision, "BLOCK")
        self.assertEqual(result.reason_code, "RETRIEVAL_FAILED")

    def test_unapproved_status_blocks(self):
        result = evaluate_policy("read_email", context(status="UNTRUSTED", trust=0.99))

        self.assertEqual(result.decision, "BLOCK")
        self.assertEqual(result.reason_code, "INVALID_CONTEXT_STATUS")

    def test_unknown_retrieval_mode_blocks(self):
        result = evaluate_policy("read_email", context(retrieval_mode="UNKNOWN"))

        self.assertEqual(result.decision, "BLOCK")
        self.assertEqual(result.reason_code, "INVALID_RETRIEVAL_MODE")


if __name__ == "__main__":
    unittest.main()
