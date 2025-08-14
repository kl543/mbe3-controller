#!/usr/bin/env python3
"""
Generate GitHub Pages site from data/ → docs/
- Copies PNG -> docs/plots/, CSV/TXT -> docs/data/
- Builds docs/index.html listing all runs (newest first) with previews & downloads
- Handles spaces/# in filenames via URL encoding
"""

import datetime
import html
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
PLOTS = DOCS / "plots"
DDATA = DOCS / "data"


def ensure_dirs():
    DOCS.mkdir(exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    DDATA.mkdir(parents=True, exist_ok=True)


def scan_and_copy():
    """Scan data/ subfolders; copy assets into docs; return run metadata."""
    runs = []
    if not DATA.exists():
        return runs

    # newest first by mtime
    subdirs = [p for p in DATA.iterdir() if p.is_dir()]
    subdirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    for d in subdirs:
        run = {"name": d.name, "pngs": [], "csvs": [], "txts": []}
        for f in sorted(d.iterdir()):
            suf = f.suffix.lower()
            if suf == ".png":
                dst = PLOTS / f.name
                shutil.copy2(f, dst)
                run["pngs"].append(dst.name)
            elif suf == ".csv":
                dst = DDATA / f.name
                shutil.copy2(f, dst)
                run["csvs"].append(dst.name)
            elif suf in (".txt",):
                dst = DDATA / f.name
                shutil.copy2(f, dst)
                run["txts"].append(dst.name)
            # ignore other files
        runs.append(run)
    return runs


def render_index(runs):
    h = lambda s: html.escape(str(s))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def img_tag(fn):
        q = quote(fn, safe="")  # encode spaces/# etc.
        return (
            f'<figure><img src="plots/{q}" alt="{h(fn)}">'
            f'<figcaption>{h(fn)}</figcaption></figure>'
        )

    def file_link(fn):
        q = quote(fn, safe="")
        return f'<li><a href="data/{q}" download>{h(fn)}</a></li>'

    cards = []
    for run in runs:
        imgs_html = "".join(img_tag(fn) for fn in run["pngs"]) or '<p class="muted">No images.</p>'
        files_html = "".join(file_link(fn) for fn in (run["csvs"] + run["txts"])) or '<li class="muted">No CSV/TXT.</li>'
        cards.append(
            f"""
            <section class="card">
              <h3>{h(run['name'])}</h3>
              <div class="grid">{imgs_html}</div>
              <h4>Downloads</h4>
              <ul>{files_html}</ul>
            </section>
            """
        )

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MBE3 Runs — Auto Index</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{--ink:#111;--muted:#666;--line:#eee}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);line-height:1.6}}
header{{background:#111;color:#fff;padding:28px 16px;text-align:center}}
main{{max-width:1100px;margin:24px auto;padding:0 16px}}
h1{{margin:0 0 6px}}
h2{{margin:20px 0 10px;border-bottom:2px solid var(--line);padding-bottom:6px}}
.card{{border:1px solid var(--line);border-radius:16px;padding:14px 16px;margin:16px 0}}
.grid{{display:grid;gap:12px}}
.grid figure{{margin:0}}
.grid img{{width:100%;border:1px solid var(--line);border-radius:12px}}
.grid figcaption{{font-size:12px;color:var(--muted);margin-top:4px;word-break:break-all}}
@media(min-width:900px){{.grid{{grid-template-columns:repeat(3,1fr)}}}}
.muted{{color:var(--muted)}}
footer{{text-align:center;color:var(--muted);padding:20px;border-top:1px solid var(--line)}}
.notice{{background:#f7f7f7;border:1px solid var(--line);padding:10px;border-radius:10px;margin-bottom:12px}}
nav a{{color:#fff;margin:0 8px}}
</style>
</head>
<body>
<header>
  <h1>MBE3 Runs</h1>
  <p class="muted">Auto-generated at {h(now)}</p>
  <nav>
    <a href="../">Repo</a>
    <a href="https://nbviewer.org/github/kl543/mbe3-controller/blob/main/auto_mbe3_control.ipynb" target="_blank" rel="noreferrer">View Notebook</a>
  </nav>
</header>
<main>
  <div class="notice">Latest runs appear first. Click CSV/TXT to download; images preview below.</div>
  {''.join(cards) if cards else '<p>No runs found yet. Push data into <code>data/</code> and re-run.</p>'}
</main>
<footer>© {now[:4]} Kaiming Liu</footer>
</body>
</html>
"""
    (DOCS / "index.html").write_text(html_doc, encoding="utf-8")


def main():
    ensure_dirs()
    runs = scan_and_copy()
    render_index(runs)
    print(f"Generated docs for {len(runs)} run(s) → {DOCS/'index.html'}")


if __name__ == "__main__":
    main()
