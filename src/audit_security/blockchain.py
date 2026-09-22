import hashlib
import json
import sqlite3
from datetime import datetime

DB_PATH = "audit_ledger.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            block_no INTEGER PRIMARY KEY,
            timestamp TEXT,
            doc_hash TEXT,
            action TEXT,
            decision TEXT,
            reason_code TEXT,
            policy_name TEXT,
            policy_version TEXT,
            trust REAL,
            prev_hash TEXT,
            latency_ms REAL,
            execution_status TEXT,
            review_id TEXT,
            security_trace_id TEXT,
            security_finding_codes TEXT,
            block_hash TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Provide a proxy object so existing code using `from ... import LEDGER` doesn't break
# if they just expect to clear it or modify it in tests
class LedgerProxy(list):
    def clear(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM blocks")
        conn.commit()
        conn.close()
        
    def __getitem__(self, idx):
        blocks = get_ledger()
        return blocks[idx]

    def __setitem__(self, idx, val):
        # Extremely hacky, but supports the test `LEDGER[0]["trust"] = 0.9`
        blocks = get_ledger()
        block = blocks[idx]
        block.update(val)
        
        # update DB
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE blocks SET trust = ?, block_hash = ? WHERE block_no = ?",
            (block["trust"], block.get("block_hash"), block["block_no"])
        )
        conn.commit()
        conn.close()

    def __len__(self):
        return len(get_ledger())

    def append(self, val):
        pass # Handled by add_to_ledger
        
    def __iter__(self):
        return iter(get_ledger())

LEDGER = LedgerProxy()


def add_to_ledger(doc_hash, result, action):
    blocks = get_ledger()
    prev_hash = blocks[-1]["block_hash"] if blocks else "0000000000000000"
    block_no = len(blocks) + 101
    
    block = {
        "block_no": block_no,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "doc_hash": doc_hash,
        "action": action,
        "decision": result["decision"],
        "reason_code": result.get("reason_code"),
        "policy_name": result.get("policy_name"),
        "policy_version": result.get("policy_version"),
        "trust": result["trust"],
        "prev_hash": prev_hash,
        "latency_ms": result["latency"],
        "execution_status": result.get("execution_status"),
        "review_id": result.get("review_id"),
        "security_trace_id": result.get("security_trace_id"),
        "security_finding_codes": [item["code"] for item in result.get("security_findings", [])] if result.get("security_findings") else [],
    }
    canonical = json.dumps(block, sort_keys=True, separators=(",", ":"))
    block["block_hash"] = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO blocks (
            block_no, timestamp, doc_hash, action, decision, reason_code, 
            policy_name, policy_version, trust, prev_hash, latency_ms, 
            execution_status, review_id, security_trace_id, security_finding_codes, block_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        block["block_no"], block["timestamp"], block["doc_hash"], block["action"],
        block["decision"], block["reason_code"], block["policy_name"], block["policy_version"],
        block["trust"], block["prev_hash"], block["latency_ms"], block["execution_status"],
        block["review_id"], block["security_trace_id"], json.dumps(block["security_finding_codes"]),
        block["block_hash"]
    ))
    conn.commit()
    conn.close()
    
    return block


def get_ledger():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blocks ORDER BY block_no ASC")
    rows = cursor.fetchall()
    conn.close()
    
    blocks = []
    for r in rows:
        block = dict(r)
        # Parse JSON array back to list
        if block["security_finding_codes"]:
            block["security_finding_codes"] = json.loads(block["security_finding_codes"])
        else:
            block["security_finding_codes"] = []
        blocks.append(block)
    return blocks


def verify_ledger():
    previous_hash = "0000000000000000"
    for block in get_ledger():
        if block.get("prev_hash") != previous_hash:
            return False
        payload = {key: value for key, value in block.items() if key != "block_hash"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        expected_hash = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        if block.get("block_hash") != expected_hash:
            return False
        previous_hash = block["block_hash"]
    return True
