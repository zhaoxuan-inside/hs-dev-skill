"""Human summaries and machine metadata share one result source."""
from . import __version__


def metadata(command, mode, trace):
    return {"skill": "hs-dev-skill", "version": __version__, "command": command,
            "mode": mode, "trace": trace}


def render(result, meta):
    banner = f"hs-dev-skill | {meta['version']} | {meta['command']} | {meta['mode']} | trace：{'on' if meta['trace'] else 'off'}"
    if isinstance(result, str):
        return banner + "\n\n" + result
    if isinstance(result, list):
        lines = []
        for row in result:
            if isinstance(row, dict) and "source" in row and "target" in row:
                lines.append(f"{row['source']} → {row['target']} ({row['kind']})")
            elif isinstance(row, dict):
                lines.append(str(row.get("path", row)) + (" · " + row["title"] if row.get("title") else ""))
            else:
                lines.append(str(row))
        return banner + "\n\n" + ("\n".join(lines) or "无结果")
    lines = [banner, "", "结果：" + ("通过" if result.get("ok", True) else "未通过")]
    for key in ("error", "route", "requires_model", "task_id", "title", "current_activity", "status",
                "operation_id", "fence", "revision", "generation", "path", "next"):
        if key in result:
            lines.append(f"{key}：{result[key]}")
    if result.get("errors"):
        lines.extend("- " + error for error in result["errors"])
    if result.get("pending_tasks"):
        lines.append("待继续或回退的任务：" + ", ".join(result["pending_tasks"]))
    if result.get("requires_model"):
        lines.append("下一步：宿主依据候选与信号作最终判断，通过 --model 提交意图及理由。")
    if result.get("missing_requirements"):
        lines.append("缺少必要上下文：" + ", ".join(result["missing_requirements"]))
    if result.get("confirmation"):
        lines.append("确认：" + str(result["confirmation"]))
    if "events" in result:
        lines.extend(f"{event['timestamp']} {event['event']} {event['attributes']}" for event in result["events"])
    if "values" in result:
        for section, values in result["values"].items():
            for key, value in values.items():
                source = result.get("sources", {}).get(section + "." + key, "default")
                lines.append(f"{section}.{key}：{value}（{source}）")
    if "text" in result:
        lines.extend(["", result["text"]])
    if "active" in result:
        for fragment in result["active"]:
            lines.extend(["", fragment["path"], fragment["text"]])
    return "\n".join(lines)
