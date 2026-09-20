import unittest

from src.blockchain import add_to_ledger, get_ledger, LEDGER
from src.agent import guarded_tool_call
from src.evaluator import evaluate_batch
from src.evaluation_cases import EVALUATION_CASES
from src.moss_validator import runtime_guard


class GuardrailTests(unittest.TestCase):
    def setUp(self):
        LEDGER.clear()

    def test_trusted_payment_is_allowed(self):
        result = runtime_guard("a1b2c3d4e5f6g7h8", "payment")

        self.assertTrue(result["allow"])
        self.assertEqual(result["decision"], "ALLOW")
        self.assertEqual(result["retrieval_mode"], "LOCAL_DEMO")

    def test_unknown_document_is_blocked(self):
        result = runtime_guard("hacker_inject_999", "payment")

        self.assertFalse(result["allow"])
        self.assertEqual(result["decision"], "BLOCK")
        self.assertIn("trust", result["reason"])

    def test_guarded_tool_does_not_execute_blocked_request(self):
        request = guarded_tool_call("payment", "hacker_inject_999")

        self.assertFalse(request["executed"])
        self.assertEqual(request["decision"], "BLOCK")

    def test_guarded_tool_executes_allowed_request(self):
        request = guarded_tool_call("payment", "a1b2c3d4e5f6g7h8")

        self.assertTrue(request["executed"])
        self.assertEqual(request["decision"], "ALLOW")

    def test_medium_trust_context_requires_review(self):
        result = runtime_guard("d4e5f6g7h8i9j0k1", "read_email")

        self.assertFalse(result["allow"])
        self.assertEqual(result["decision"], "REVIEW")
        self.assertIn("autonomous", result["reason"])

    def test_evaluation_reports_real_counts(self):
        cases = [
            {"doc_hash": "a1b2c3d4e5f6g7h8", "name": "trusted", "expected": "ALLOW"},
            {"doc_hash": "d4e5f6g7h8i9j0k1", "name": "review", "action": "read_email", "expected": "REVIEW"},
            {"doc_hash": "tampered_amt_1", "name": "tampered", "expected": "BLOCK"},
        ]

        report = evaluate_batch(cases, runtime_guard)

        self.assertEqual(report["total_cases"], 3)
        self.assertEqual(report["blocked"], 1)
        self.assertEqual(report["passed"], 3)
        self.assertEqual(report["accuracy"], 1.0)
        self.assertGreaterEqual(report["p95_latency_ms"], report["median_latency_ms"])

    def test_large_evaluation_corpus(self):
        report = evaluate_batch(EVALUATION_CASES, runtime_guard)

        self.assertEqual(report["total_cases"], 12)
        self.assertEqual(report["passed"], 12)
        self.assertEqual(report["accuracy"], 1.0)
        self.assertIn("prompt_injection", report["category_results"])
        self.assertIn("tampering", report["category_results"])

    def test_audit_chain_links_blocks(self):
        first = add_to_ledger("first", runtime_guard("hacker_inject_999", "payment"), "payment")
        second = add_to_ledger("second", runtime_guard("hacker_inject_999", "payment"), "payment")

        self.assertEqual(first["decision"], "BLOCK")
        self.assertEqual(second["prev_hash"], first["block_hash"])
        self.assertEqual(len(get_ledger()), 2)

    def test_audit_entries_keep_color_codable_decisions(self):
        allowed = add_to_ledger("allowed", runtime_guard("a1b2c3d4e5f6g7h8", "payment"), "payment")
        review = add_to_ledger("review", runtime_guard("d4e5f6g7h8i9j0k1", "read_email"), "read_email")
        blocked = add_to_ledger("blocked", runtime_guard("hacker_inject_999", "payment"), "payment")

        self.assertEqual([allowed["decision"], review["decision"], blocked["decision"]], ["ALLOW", "REVIEW", "BLOCK"])


if __name__ == "__main__":
    unittest.main()
