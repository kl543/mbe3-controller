#!/usr/bin/env python3
import os, shutil, html, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
PLOTS = DOCS / "plots"
DDATA = DOCS / "data"

def copy_assets():
    DOCS.mkdir(exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    DDATA.mkdir(parents=True, exist_ok=True)

    runs = []
    if not DATA.exists():
        return runs

    for d in sorted([p for p in DATA.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True):
        run = {"name": d.name, "pngs": [], "csvs": [], "txts": []}
        for f in d.iterdir():
            if f.suffix.lower() == ".png":
                dst = PLOTS / f.name
                shutil.copy2(f, dst)
                run["pngs"].append(dst.name)
            elif f.suffix.lower() == ".csv":
                dst = DDATA / f.name
                shutil.copy2(f, dst)
                run["csvs"].append(dst.name)
            elif f.suffix.lower() in (".txt",):
                dst = DDATA / f.name
                shutil.copy2(f, dst)
                run["txts"].append(dst.name)
        runs.append(run)
    return runs

def render_index(runs):
    def h(s): return html.escape(str(s))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    cards_html = []
    for run in runs:
        imgs = "".join(
            f'<figure><img src="plots/{h(fn)}" alt="{h(fn)}"><figcaption>{h(fn)}</figcaption></figure>'
            for fn in run["pngs"]
        )
        files = "".join(
            f'<li><a href="data/{h(fn)}" download>{h(fn)}</a></li>'
            for fn in run["csvs"] + run["txts"]
        )
        cards_html.append(f"""
        <section class="card">
          <h3>{h(run['name'])}</h3>
          <div class="grid">{imgs or '<p class="muted">No images found.</p>'}</div>
          <h4>Downloads</h4>
          <ul>{files or '<li class="muted">No CSV/TXT found.</li>'}</ul>
        </section>
        """)

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MBE3 Runs — Auto Index</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{--ink:#111;--muted:#666;--line:#eee}}
body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);line-height:1.6}}
header{{background:#111;color:#fff;padding:28px 16px;text-align:center}}
main{{max-width:1100px;margin:24px auto;padding:0 16px}}
h1{{margin:0 0 6px}}
h2{{margin:20px 0 10px;border-bottom:2px solid var(--line);padding-bottom:6px}}
h3{{margin:0 0 6px}}
.card{{border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin:16px 0}}
.grid{{display:grid;gap:12px}}
.grid figure{{margin:0}}
.grid img{{width:100%;border:1px solid var(--line);border-radius:12px}}
.grid figcaption{{font-size:12px;color:var(--muted);margin-top:4px;word-break:break-all}}
@media(min-width:900px){{.grid{{grid-template-columns:repeat(3,1fr)}}}}
.muted{{color:var(--muted)}}
footer{{text-align:center;color:var(--muted);padding:20px}}
.notice{{background:#f7f7f7;border:1px solid var(--line);padding:10px;border-radius:10px}}
nav a{{margin-right:12px}}
</style>
</head>
<body>
<header>
  <h1>MBE3 Runs</h1>
  <p class="muted">Auto-generated at {h(now)}</p>
  <nav>
    <a href="../">Repo</a>
    <a href="https://nbviewer.org/github/kl543/mbe3-controller/blob/main/auto_mbe3_control.ipynb" target="_blank">View Notebook</a>
  </nav>
</header>
<main>
  <div class="notice">Latest runs appear first. Click CSV/TXT to download; images preview below.</div>
  {"".join(cards_html) or "<p>No runs found yet. Push data into <code>data/</code>.</p>"}
</main>
<footer>© {now[:4]} Kaiming Liu</footer>
</body>
</html>"""
    (DOCS / "index.html").write_text(html_doc, encoding="utf-8")

if __name__ == "__main__":
    runs = copy_assets()
    render_index(runs)
    print(f"Generated docs with {len(runs)} run(s). Open docs/index.html.")
