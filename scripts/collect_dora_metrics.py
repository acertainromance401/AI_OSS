import json
import os
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen


def parse_iso8601(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def github_get(url: str, token: str):
    req = Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    with urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    lookback_days = int(os.getenv("LOOKBACK_DAYS", "7"))

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=lookback_days)

    owner, repo = repository.split("/")
    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    pulls = github_get(f"{base_url}/pulls?state=closed&sort=updated&direction=desc&per_page=100", token)
    merged_pulls = []
    lead_times_hours = []

    for pull in pulls:
        merged_at = pull.get("merged_at")
        created_at = pull.get("created_at")
        if not merged_at or not created_at:
            continue

        merged_dt = parse_iso8601(merged_at)
        if merged_dt < since:
            continue

        created_dt = parse_iso8601(created_at)
        lead_time_hours = (merged_dt - created_dt).total_seconds() / 3600
        lead_times_hours.append(lead_time_hours)
        merged_pulls.append(pull)

    lead_time_avg_hours = round(sum(lead_times_hours) / len(lead_times_hours), 2) if lead_times_hours else None

    deployments = github_get(f"{base_url}/deployments?per_page=100", token)
    deployment_events = []

    for deployment in deployments:
        deployment_id = deployment["id"]
        statuses = github_get(f"{base_url}/deployments/{deployment_id}/statuses?per_page=1", token)
        if not statuses:
            continue

        latest = statuses[0]
        status_time = parse_iso8601(latest["created_at"])
        if status_time < since:
            continue

        deployment_events.append(
            {
                "deployment_id": deployment_id,
                "state": latest["state"],
                "time": status_time,
            }
        )

    deployment_events.sort(key=lambda event: event["time"])

    success_states = {"success"}
    failure_states = {"failure", "error"}

    total_deployments = len(deployment_events)
    successful_deployments = sum(1 for event in deployment_events if event["state"] in success_states)
    failed_deployments = sum(1 for event in deployment_events if event["state"] in failure_states)

    change_failure_rate = round((failed_deployments / total_deployments) * 100, 2) if total_deployments else None
    deployment_frequency_per_week = successful_deployments

    success_times = [event["time"] for event in deployment_events if event["state"] in success_states]
    mttr_hours_samples = []

    for failed_event in [event for event in deployment_events if event["state"] in failure_states]:
        recovery_candidates = [time for time in success_times if time > failed_event["time"]]
        if recovery_candidates:
            recovery_time = recovery_candidates[0]
            mttr_hours_samples.append((recovery_time - failed_event["time"]).total_seconds() / 3600)

    mttr_hours = round(sum(mttr_hours_samples) / len(mttr_hours_samples), 2) if mttr_hours_samples else None

    metrics = {
        "generated_at": now.isoformat(),
        "period": {
            "lookback_days": lookback_days,
            "since": since.isoformat(),
            "until": now.isoformat(),
        },
        "repository": repository,
        "dora_metrics": {
            "lead_time_for_changes_hours_avg": lead_time_avg_hours,
            "deployment_frequency_per_week": deployment_frequency_per_week,
            "change_failure_rate_percent": change_failure_rate,
            "mttr_hours_avg": mttr_hours,
        },
        "counts": {
            "merged_prs": len(merged_pulls),
            "total_deployments": total_deployments,
            "successful_deployments": successful_deployments,
            "failed_deployments": failed_deployments,
        },
    }

    os.makedirs("metrics", exist_ok=True)
    with open("metrics/dora_metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics, file, ensure_ascii=False, indent=2)

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
