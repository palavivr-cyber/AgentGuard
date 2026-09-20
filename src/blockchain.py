import hashlib
import json
import time
from datetime import datetime

LEDGER = []

def add_to_ledger(doc_hash, result, action):
    prev_hash = LEDGER[-1]["block_hash"] if LEDGER else "0000000000000000"
    block = {
        "block_no": len(LEDGER) + 101,
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
    }
    canonical = json.dumps(block, sort_keys=True, separators=(",", ":"))
    block["block_hash"] = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    LEDGER.append(block)
    return block

def get_ledger():
    return LEDGER


def verify_ledger():
    previous_hash = "0000000000000000"
    for block in LEDGER:
        if block.get("prev_hash") != previous_hash:
            return False
        payload = {key: value for key, value in block.items() if key != "block_hash"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        expected_hash = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        if block.get("block_hash") != expected_hash:
            return False
        previous_hash = block["block_hash"]
    return True