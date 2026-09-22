import time


TRUSTED_DB = {
    "a1b2c3d4e5f6g7h8": {"name": "Invoice INV100 - HAL Vendor ABC - $5000", "trust": 0.95, "vendor": "HAL"},
    "b2c3d4e5f6g7h8i9": {"name": "PO #PO2024 - Verified Supplier", "trust": 0.93, "vendor": "SafeCorp"},
    "d4e5f6g7h8i9j0k1": {"name": "Invoice INV104 - New Vendor - $1200", "trust": 0.82, "vendor": "NewVendor"},
}


def local_demo_search(doc_hash):
    start = time.perf_counter_ns()
    data = TRUSTED_DB.get(doc_hash)
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
