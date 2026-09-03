from __future__ import annotations

import json
from datetime import date, timedelta
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "assets" / "contrib-heatmap.svg"

PALETTE_LIGHT = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
PALETTE_DARK = ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"]


def parse_day(item):
    return (
        date.fromisoformat(item["date"]),
        int(item.get("count", 0)),
        max(0, min(4, int(item.get("level", 0)))),
    )


def sunday(day: date) -> date:
    return day - timedelta(days=(day.weekday() + 1) % 7)


def streaks(items):
    counts = {d: c for d, c, _ in items}
    if not counts:
        return 0, 0

    cursor = max(counts)
    if counts.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)

    current = 0
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    longest = 0
    run = 0
    for day in sorted(counts):
        if counts[day] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    return current, longest


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    items = sorted(parse_day(item) for item in payload["days"])

    week_starts = sorted({sunday(d) for d, _, _ in items})[-53:]
    allowed = set(week_starts)
    visible = [(d, c, l) for d, c, l in items if sunday(d) in allowed]
    week_index = {week: index for index, week in enumerate(week_starts)}

    total = sum(count for _, count, _ in visible)
    active = sum(1 for _, count, _ in visible if count > 0)
    current, longest = streaks(visible)
    best = max(visible, key=lambda row: row[1]) if visible else (date.today(), 0, 0)

    cells = []
    for day, count, level in visible:
        column = week_index[sunday(day)]
        row = (day.weekday() + 1) % 7
        x = 57 + column * 15
        y = 38 + row * 15
        delay = (column + row) * 0.006
        title = escape(f"{count} contributions on {day.isoformat()}")
        cells.append(
            f'<g><title>{title}</title><rect x="{x}" y="{y}" width="11" height="11" rx="2" '
            f'class="lv{level} cell" style="animation-delay:{delay:.3f}s"/></g>'
        )

    month_labels = []
    seen_months = set()
    for week in week_starts:
        key = (week.year, week.month)
        if key in seen_months:
            continue
        seen_months.add(key)
        x = 57 + week_index[week] * 15
        month_labels.append(f'<text x="{x}" y="25" font-size="10" class="muted">{week.strftime("%b")}</text>')

    light_classes = "".join(f".lv{i}{{fill:{color}}}" for i, color in enumerate(PALETTE_LIGHT))
    dark_classes = "".join(f".lv{i}{{fill:{color}}}" for i, color in enumerate(PALETTE_DARK))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="190" viewBox="0 0 860 190">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}}
.fg{{fill:#24292f}} .muted{{fill:#57606a}} {light_classes}
.cell{{opacity:0;transform:translateY(-5px);animation:drop .24s ease-out forwards}}
@keyframes drop{{to{{opacity:1;transform:translateY(0)}}}}
@media(prefers-color-scheme:dark){{.fg{{fill:#e6edf3}}.muted{{fill:#8b949e}}{dark_classes}}}
</style>
<text x="14" y="19" font-size="11" class="muted">last 53 weeks · refreshed automatically from GitHub public contribution data</text>
{''.join(month_labels)}
<text x="14" y="50" font-size="10" class="muted">Sun</text><text x="14" y="80" font-size="10" class="muted">Tue</text><text x="14" y="110" font-size="10" class="muted">Thu</text><text x="14" y="140" font-size="10" class="muted">Sat</text>
{''.join(cells)}
<text x="14" y="173" font-size="11" class="fg">{total:,} contributions · {active} active days · current streak {current}d · longest {longest}d · best day {best[1]}</text>
<text x="700" y="173" font-size="10" class="muted">Less</text>
<rect x="730" y="164" width="10" height="10" rx="2" class="lv0"/><rect x="744" y="164" width="10" height="10" rx="2" class="lv1"/><rect x="758" y="164" width="10" height="10" rx="2" class="lv2"/><rect x="772" y="164" width="10" height="10" rx="2" class="lv3"/><rect x="786" y="164" width="10" height="10" rx="2" class="lv4"/><text x="802" y="173" font-size="10" class="muted">More</text>
</svg>'''

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
