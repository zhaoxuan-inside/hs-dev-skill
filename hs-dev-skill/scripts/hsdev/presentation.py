"""Opt-in console summaries; execution records remain complete and authoritative."""


def compact_result(command, result, delivery=None):
    if command not in {"run", "resume", "status", "plan", "lock"} or not isinstance(result, dict):
        return result
    keys = ("ok", "version", "delivery", "activity", "scope", "status", "plan_digest", "unchanged",
            "source_drift", "next_action", "coordination", "token")
    summary = {key: result[key] for key in keys if key in result}
    summary["compact"] = True
    delivery = result.get("delivery") or delivery
    if delivery:
        summary["delivery"] = delivery
        summary["state_path"] = f"hs-dev/execution/deliveries/{delivery}.json"
    for key in ("sources", "tracked", "paths", "outputs", "questions", "prior_questions"):
        if key in result:
            summary[key + "_count"] = len(result[key])
    if "questions" in result:
        summary["question_refs"] = [{"id": key, "blocking": row.get("blocking", True)}
                                    for key, row in list(result["questions"].items())[:20]]
    if "results" in result:
        summary["results"] = [{key: row[key] for key in
                               ("id", "exit_code", "path", "digest", "timeout_seconds", "elapsed_seconds") if key in row}
                              for row in result["results"]]
        summary["passed_checks"] = sum(row["exit_code"] == 0 for row in result["results"])
        summary["check_count"] = len(result["results"])
    if "readiness" in result:
        readiness = result["readiness"]
        summary["ready"] = readiness["ok"]
        issues = readiness.get("issues", [])
        summary["issues_count"] = len(issues)
        summary["issues"] = [issue[:400] for issue in issues[:20]]
        if not readiness["ok"] and not result.get("source_drift"):
            summary["next_action"] = "Review readiness issues; pause only work that depends on them."
    if "lock" in result:
        lock = result["lock"]
        summary["lock"] = {key: lock[key] for key in ("delivery", "token", "locked_at") if key in lock} if lock else None
    if "deliveries" in result:
        summary["deliveries_count"] = len(result["deliveries"])
        summary["deliveries"] = [{key: row[key] for key in ("id", "activity", "status")}
                                 for row in result["deliveries"][:50]]
    if "plan" in result and result["plan"]:
        summary["plan_digest"] = result["plan"]["digest"]
    summary["details"] = "Omit --compact to read the complete response; stored records and evidence are unchanged."
    return summary
