import hashlib
import time
from datetime import datetime

LEDGER = []

def add_to_ledger(doc_hash, result, action):
    block_hash = hashlib.sha256(f"{doc_hash}{time.time()}".encode()).hexdigest()[:16]
    prev_hash = LEDGER[-1]["block_hash"] if LEDGER else "0000000000000000"
    block = {
        "block_no": len(LEDGER) + 101,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "doc_hash": doc_hash,
        "action": action,
        "decision": result["action"],
        "trust": result["trust"],
        "block_hash": block_hash,
        "prev_hash": prev_hash,
        "latency_ms": result["latency"]
    }
    LEDGER.append(block)
    return block

def get_ledger():
    return LEDGER