import unittest

from src.blockchain import LEDGER, add_to_ledger, verify_ledger
from src.honeypot import honeypot_trap


class AuditSecurityTests(unittest.TestCase):
    def setUp(self):
        LEDGER.clear()

    def test_audit_chain_detects_tampering(self):
        add_to_ledger(
            "doc-1",
            {"decision": "BLOCK", "trust": 0.1, "latency": 1.0},
            "payment",
        )
        self.assertTrue(verify_ledger())

        LEDGER[0]["trust"] = 0.9

        self.assertFalse(verify_ledger())

    def test_security_trace_is_only_for_suspicious_blocks(self):
        suspicious = honeypot_trap("hacker_inject_999", True)
        ordinary_block = honeypot_trap("unknown-document", True)
        review = honeypot_trap("stale-review", False)

        self.assertTrue(suspicious["activated"])
        self.assertEqual(suspicious["telemetry_mode"], "DEMO")
        self.assertFalse(ordinary_block["activated"])
        self.assertFalse(review["activated"])


if __name__ == "__main__":
    unittest.main()