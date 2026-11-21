def summarize_results(results: list) -> dict:
    passed, failed, errors, unknown = 0, 0, 0, 0
    unknown_statuses = []
    
    for result in results:
        if result["status"] == "PASS":
            passed += 1
        elif result["status"] == "FAIL":
            failed += 1
        elif result["status"] == "ERROR":
            errors += 1
        else:
            unknown += 1
            if result["status"] not in unknown_statuses:
                unknown_statuses.append(result["status"]) 
    
    
    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "unknown": unknown,
        "unknown_statuses": unknown_statuses,
        "summary_status": "INCOMPLETE" if unknown > 0 else "COMPLETE"
    }