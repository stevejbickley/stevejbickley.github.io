"""Refresh public counters; private/entitled metrics retain dated snapshots."""
import json
from pathlib import Path
from metrics import load_metrics, refresh

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    data = load_metrics(root)
    successes, failures = refresh(data)
    for source in successes:
        print(f"Updated {source}: {data[source]['checked_at']}")
    for source, reason in failures:
        print(f"::warning title=Metric refresh unavailable::{source}: {reason}; previous snapshot retained")
    if not successes:
        raise SystemExit("No public source could be refreshed; existing metrics were preserved")
    (root / "data/research-metrics.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
