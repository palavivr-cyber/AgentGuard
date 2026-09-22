import time
import sqlite3
import os

DB_PATH = "local_fallback.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trusted_docs (
            doc_hash TEXT PRIMARY KEY,
            name TEXT,
            trust REAL,
            vendor TEXT
        )
    """)
    
    # Check if empty
    cursor.execute("SELECT COUNT(*) FROM trusted_docs")
    if cursor.fetchone()[0] == 0:
        default_docs = [
            ("a1b2c3d4e5f6g7h8", "Invoice INV100 - HAL Vendor ABC - $5000", 0.95, "HAL"),
            ("b2c3d4e5f6g7h8i9", "PO #PO2024 - Verified Supplier", 0.93, "SafeCorp"),
            ("d4e5f6g7h8i9j0k1", "Invoice INV104 - New Vendor - $1200", 0.82, "NewVendor"),
        ]
        cursor.executemany("INSERT INTO trusted_docs VALUES (?, ?, ?, ?)", default_docs)
        conn.commit()
    conn.close()

# Initialize on module load
init_db()

def _get_doc(doc_hash):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, trust, vendor FROM trusted_docs WHERE doc_hash = ?", (doc_hash,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"name": row[0], "trust": row[1], "vendor": row[2]}
    return None

def local_demo_search(doc_hash):
    start = time.perf_counter_ns()
    data = _get_doc(doc_hash)
    latency = round((time.perf_counter_ns() - start) / 1_000_000, 4)
    if data:
        return {
            "found": True,
            "trust": data["trust"],
            "latency": latency,
            "doc": data["name"],
            "status": "VERIFIED",
            "vendor": data["vendor"],
            "retrieval_mode": "LOCAL_DEMO",
        }
    return {
        "found": False,
        "trust": 0.12,
        "latency": latency,
        "doc": "UNKNOWN / TAMPERED",
        "status": "UNTRUSTED",
        "vendor": "UNKNOWN",
        "retrieval_mode": "LOCAL_DEMO",
    }


def moss_error_result(latency=0.0):
    return {
        "found": False,
        "trust": 0.0,
        "latency": latency,
        "doc": "MOSS RETRIEVAL FAILED",
        "status": "UNTRUSTED",
        "vendor": "UNKNOWN",
        "retrieval_mode": "MOSS_ERROR",
    }
