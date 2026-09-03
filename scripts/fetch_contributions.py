from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from profile_config import USERNAME

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"
HEADERS = {"User-Agent": f"{USERNAME}-profile-readme/1.0", "Accept": "text/html"}
COUNT_RE = re.compile(r"([\d,]+)\s+contribution", re.I)


def count_from_text(text: str) -> int | None:
    text = " ".join(text.split())
    if "no contributions" in text.lower():
        return 0
    match = COUNT_RE.search(text)
    return int(match.group(1).replace(",", "")) if match else None


def main() -> None:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    tooltip_counts: dict[str, int] = {}
    for tip in soup.find_all(["tool-tip", "span"]):
        target = tip.get("for") or tip.get("id")
        if not target:
            continue
        count = count_from_text(tip.get_text(" ", strip=True))
        if count is not None:
            tooltip_counts[str(target)] = count

    by_date: dict[str, dict] = {}
    for node in soup.select("[data-date]"):
        day = node.get("data-date")
        if not day or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            continue

        try:
            level = max(0, min(4, int(node.get("data-level") or 0)))
        except ValueError:
            level = 0

        count = None
        raw_count = node.get("data-count")
        if raw_count is not None and str(raw_count).isdigit():
            count = int(raw_count)

        if count is None and node.get("aria-label"):
            count = count_from_text(str(node.get("aria-label")))

        if count is None:
            node_id = node.get("id")
            described = node.get("aria-describedby") or node.get("aria-labelledby")
            for key in (node_id, described):
                if key and key in tooltip_counts:
                    count = tooltip_counts[key]
                    break

        if count is None and node.get("id"):
            tip = soup.find("tool-tip", attrs={"for": node.get("id")})
            if tip:
                count = count_from_text(tip.get_text(" ", strip=True))

        by_date[day] = {"date": day, "count": 0 if count is None else count, "level": level}

    if not by_date:
        raise RuntimeError("No contribution day cells were found in GitHub's public contribution fragment.")

    payload = {
        "username": USERNAME,
        "source": URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "days": [by_date[d] for d in sorted(by_date)],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {len(payload['days'])} contribution days to {OUT}")


if __name__ == "__main__":
    main()
