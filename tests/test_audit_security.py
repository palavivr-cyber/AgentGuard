import unittest
import sqlite3
from src.blockchain import LEDGER, add_to_ledger, verify_ledger, DB_PATH
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

        # Tamper directly in the SQLite database to simulate an attack
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE blocks SET trust = 0.9 WHERE doc_hash = 'doc-1'")
        conn.commit()
        conn.close()

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