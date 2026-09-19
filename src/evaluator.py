from statistics import mean, median


def percentile(values, percentile_rank):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * percentile_rank / 100
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def evaluate_batch(test_cases, guard_fn):
    results = []
    for case in test_cases:
        doc_hash = case["doc_hash"]
        name = case["name"]
        action = case.get("action", "payment")
        expected = case.get("expected")
        result = guard_fn(doc_hash, action)
        results.append(
            {
                "name": name,
                "category": case.get("category", "uncategorized"),
                "expected": expected,
                "actual": result["decision"],
                "passed": expected is None or expected == result["decision"],
                "latency_ms": result["latency"],
                "result": result,
            }
        )

    latencies = [item["latency_ms"] for item in results]
    passed = sum(item["passed"] for item in results)
    blocked = sum(item["actual"] == "BLOCK" for item in results)
    category_results = {}
    for item in results:
        category = item["category"]
        category_results.setdefault(category, {"total": 0, "passed": 0})
        category_results[category]["total"] += 1
        category_results[category]["passed"] += int(item["passed"])

    for values in category_results.values():
        values["accuracy"] = round(values["passed"] / values["total"], 3)

    return {
        "blocked": blocked,
        "total_cases": len(results),
        "passed": passed,
        "accuracy": round(passed / len(results), 3) if results else 0.0,
        "average_latency_ms": round(mean(latencies), 3) if latencies else 0.0,
        "median_latency_ms": round(median(latencies), 3) if latencies else 0.0,
        "p95_latency_ms": round(percentile(latencies, 95), 3) if latencies else 0.0,
        "category_results": category_results,
        "results": results,
    }