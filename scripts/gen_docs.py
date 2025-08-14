#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a simple docs/index.html for GitHub Pages.

- Scans ./data/* subfolders
- Shows PNG previews (figures) and provides links to CSV/TXT/PNG files
- Injects the global header from the main site (/_site-header.html)
"""

import os, sys, html, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # repo root
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

HEADER_INJECT = """
<div id="global-header"></div>
<script>
  fetch('/_site-header.html')
    .then(r => r.text())
    .then(h => { document.getElementById('global-header').outerHTML = h; });
</script>
"""

def find_runs(base: Path):
    """Return a list of (run_name, files_dict) sorted by name desc."""
    runs = []
    if not base.exists():
        return runs
    for p in base.iterdir():
        if p.is_dir():
            files = [f for f in p.iterdir() if f.is_file()]
            files.sort()
            runs.append((p.name, files))
    # newest first by name (your run folders看起来按日期开头)
    runs.sort(key=lambda x: x[0], reverse=True)
    return runs

def link(relpath: str, label: str):
    return f'<a class="pill" href="{html.escape(relpath)}">{html.escape(label)}</a>'

def build_html():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    runs = find_runs(DATA_DIR)

    sections = []
    for run_name, files in runs:
        # split by ext
        pngs = [f for f in files if f.suffix.lower()==".png"]
        csvs = [f for f in files if f.suffix.lower()==".csv"]
        txts = [f for f in files if f.suffix.lower() in (".txt",".log")]

        # file links row
        links = []
        for f in csvs: links.append(link(str(f.relative_to(ROOT)), f.name))
        for f in txts: links.append(link(str(f.relative_to(ROOT)), f.name))
        files_row = " ".join(links) if links else '<span class="muted">No CSV/TXT</span>'

        # image grid
        cards = []
        for png in pngs:
            rel = str(png.relative_to(ROOT))
            cards.append(
                f"""<figure>
                      <img src="{html.escape(rel)}" alt="{html.escape(png.name)}">
                      <figcaption>{html.escape(png.name)}</figcaption>
                    </figure>"""
            )
        grid = "\n".join(cards) if cards else '<div class="muted">No figures found.</div>'

        sections.append(f"""
        <section class="section card">
          <h2 style="margin-bottom:8px">{html.escape(run_name)}</h2>
          <div class="row" style="margin-bottom:12px">{files_row}</div>
          <div class="gallery">{grid}</div>
        </section>
        """)

    sections_html = "\n".join(sections) if sections else """
      <section class="section card"><div class="muted">No runs under <code>data/</code> yet.</div></section>
    """

    html_out = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MBE3 Runs</title>
  <style>
    :root{{--ink:#111;--muted:#6b6b6b;--line:#e9e9e9;--bg:#fafafa;--card:#fff}}
    html,body{{margin:0;background:var(--bg);color:var(--ink);
      font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}}
    .hero{{background:#111;color:#fff;padding:40px 16px 36px}}
    .wrap{{max-width:1040px;margin:0 auto;padding:0 16px}}
    h1{{margin:0 0 6px;font-size:28px}}
    .sub{{color:#cfcfcf}}
    .section{{margin:22px 0 28px}}
    .card{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px 18px}}
    .row{{display:flex;gap:10px;flex-wrap:wrap;align-items:center}}
    .pill{{display:inline-block;border:1px solid var(--line);padding:6px 10px;border-radius:10px;text-decoration:none;color:var(--ink)}}
    .pill:hover{{background:#f6f6f6}}
    .muted{{color:var(--muted)}}
    h2{{margin:0 0 12px;font-size:22px}}
    .gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}
    figure{{margin:0;border:1px solid var(--line);background:#fff;border-radius:12px;overflow:hidden}}
    figure img{{display:block;width:100%;height:auto}}
    figcaption{{font-size:14px;color:var(--muted);padding:8px 10px;border-top:1px solid var(--line)}}
  </style>
</head>
<body>
{HEADER_INJECT}

<div class="hero">
  <div class="wrap">
    <h1>MBE3 Runs</h1>
    <div class="sub">Auto-generated at {now}</div>
  </div>
</div>

<main class="wrap">
  <div class="section card" style="margin-top:20px">
    Latest runs appear first. Click CSV/TXT to download; images preview below.
  </div>
  {sections_html}
</main>

</body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(html_out, encoding="utf-8")
    print(f"[OK] Wrote {DOCS_DIR/'index.html'}")

if __name__ == "__main__":
    build_html()
