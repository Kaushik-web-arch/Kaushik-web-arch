from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "info-card.svg"

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="510" height="360" viewBox="0 0 510 360">
<style>
text{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace}.fg{fill:#24292f}.muted{fill:#57606a}.green{fill:#1a7f37}@media(prefers-color-scheme:dark){.fg{fill:#e6edf3}.muted{fill:#8b949e}.green{fill:#3fb950}}.row{opacity:0;animation:in .28s forwards}@keyframes in{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
</style>
<text x="18" y="27" font-size="13" class="green">kaushik@github</text><text x="18" y="48" font-size="12" class="muted">────────────────────────────────────────────────────</text>
<g font-size="12.5">
<g class="row" style="animation-delay:.10s"><text x="18" y="76" class="green">role</text><text x="116" y="76" class="fg">CS (Data Science) Undergraduate</text></g>
<g class="row" style="animation-delay:.18s"><text x="18" y="103" class="green">focus</text><text x="116" y="103" class="fg">Software Development + AI</text></g>
<g class="row" style="animation-delay:.26s"><text x="18" y="130" class="green">languages</text><text x="116" y="130" class="fg">Python · Java · C · SQL</text></g>
<g class="row" style="animation-delay:.34s"><text x="18" y="157" class="green">core_cs</text><text x="116" y="157" class="fg">DSA · OOP · DBMS</text></g>
<g class="row" style="animation-delay:.42s"><text x="18" y="184" class="green">backend</text><text x="116" y="184" class="fg">Flask · Streamlit</text></g>
<g class="row" style="animation-delay:.50s"><text x="18" y="211" class="green">databases</text><text x="116" y="211" class="fg">MySQL · SQLite · PostgreSQL</text></g>
<g class="row" style="animation-delay:.58s"><text x="18" y="238" class="green">ai_ml</text><text x="116" y="238" class="fg">Machine Learning · LLMs · Agentic AI</text></g>
<g class="row" style="animation-delay:.66s"><text x="18" y="265" class="green">tools</text><text x="116" y="265" class="fg">Git · GitHub · VS Code</text></g>
<g class="row" style="animation-delay:.74s"><text x="18" y="292" class="green">deploy</text><text x="116" y="292" class="fg">Railway · Supabase</text></g>
<g class="row" style="animation-delay:.82s"><text x="18" y="319" class="green">location</text><text x="116" y="319" class="fg">Bengaluru, India</text></g>
</g><rect x="18" y="338" width="8" height="13" class="green"><animate attributeName="opacity" values="1;0;1" dur=".9s" repeatCount="indefinite"/></rect></svg>'''

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(SVG, encoding="utf-8")
print(f"Wrote {OUT}")
