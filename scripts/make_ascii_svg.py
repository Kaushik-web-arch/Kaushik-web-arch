from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageEnhance, ImageOps

from profile_config import USERNAME

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "kaushik-ascii.svg"
AVATAR_URL = f"https://github.com/{USERNAME}.png?size=460"
RAMP = "@%#*+=-:. "  # dark -> bright
COLS = 58
ROWS = 34


def main() -> None:
    response = requests.get(
        AVATAR_URL,
        headers={"User-Agent": f"{USERNAME}-profile-readme/1.0"},
        timeout=30,
    )
    response.raise_for_status()

    image = Image.open(BytesIO(response.content)).convert("RGB")
    image = ImageOps.fit(image, (460, 460), method=Image.Resampling.LANCZOS)
    gray = ImageOps.autocontrast(ImageOps.grayscale(image))
    gray = ImageEnhance.Contrast(gray).enhance(1.25)
    small = gray.resize((COLS, ROWS), Image.Resampling.BILINEAR)
    pixels = small.load()

    cx, cy = (COLS - 1) / 2, (ROWS - 1) / 2
    rx, ry = COLS * 0.49, ROWS * 0.49
    lines: list[str] = []

    for y in range(ROWS):
        chars: list[str] = []
        for x in range(COLS):
            # Circular crop removes the hard square edge of the profile avatar.
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 1:
                chars.append(" ")
                continue
            value = pixels[x, y]
            index = round((value / 255) * (len(RAMP) - 1))
            chars.append(RAMP[index])
        lines.append("".join(chars).rstrip())

    width, height = 350, 360
    x0, y0, line_height = 15, 44, 8.25
    wipe_width = 325
    definitions: list[str] = []
    text_rows: list[str] = []

    for i, line in enumerate(lines):
        y = y0 + i * line_height
        clip_id = f"row-{i}"
        begin = 0.035 * i
        definitions.append(
            f'<clipPath id="{clip_id}"><rect x="{x0}" y="{y-line_height+1:.1f}" width="0" height="{line_height+2:.1f}">'
            f'<animate attributeName="width" from="0" to="{wipe_width}" begin="{begin:.3f}s" dur=".32s" fill="freeze"/>'
            f'</rect></clipPath>'
        )
        text_rows.append(
            f'<text x="{x0}" y="{y:.1f}" font-size="7.8" class="ascii" '
            f'clip-path="url(#{clip_id})" xml:space="preserve">{escape(line)}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="350" height="360" viewBox="0 0 350 360">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}}
.ascii{{fill:#57606a}} .green{{fill:#1a7f37}}
@media(prefers-color-scheme:dark){{.ascii{{fill:#c9d1d9}}.green{{fill:#3fb950}}}}
</style>
<defs>{''.join(definitions)}</defs>
<text x="12" y="18" font-size="11" class="green"># github_avatar → ascii.svg</text>
{''.join(text_rows)}
<rect x="12" y="337" width="8" height="13" class="green"><animate attributeName="opacity" values="1;0;1" dur=".9s" repeatCount="indefinite"/></rect>
</svg>'''

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
