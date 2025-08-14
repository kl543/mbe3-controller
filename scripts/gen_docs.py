#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate MBE runs page (index.html):
- Traverse data/<run_name>/, preview PNG images in a grid,
  and list downloads (CSV/TXT/etc.) for that run.
- Use shared _site-header.html if present, else fallback header.
- Keep links in same tab; include "Back to Projects" up top.
"""

import os
from datetime import datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
DATA_DIR = os.path.join(ROOT, "data")
OUT_HTML = os.path.join(ROOT, "index.html")

MAIN_SITE = "https://kl543.github.io"
PROJECTS_URL = f"{MAIN_SITE}/projects.html"

def load_site_header():
    candidates = [
        os.path.join(ROOT, "_site-header.html"),
        os.path.join(os.path.dirname(ROOT), "_site-header.html"),
    ]
    for p in candidates:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    # fallback header
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>MBE3 Runs — Kaiming Liu</title>
<style>
:root{{--line:#e9e9e9;--muted:#666;--ink:#111}}
body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);line-height:1.6}}
header{{background:#111;color:#fff;padding:30px 16px;text-align:center}}
nav{{display:flex;gap:14px;justify-content:center;margin:10px 0 0}}
nav a{{color:#fff;text-decoration:none;opacity:.9}} nav a:hover{{opacity:1}}
.container{{max-width:1160px;margin:24px auto;padding:0 16px}}
.muted{{color:var(--muted)}}
.card{{border:1px solid var(--line);border-radius:16px;padding:16px 18px;margin:16px 0;background:#fff}}
h1,h2,h3{{margin:.2rem 0 .6rem}}
.btn{{display:inline-block;border:1px solid var(--line);padding:8px 12px;border-radius:10px;text-decoration:none;margin-right:8px;color:#111}}
.btn:hover{{background:#f6f6f6}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}}
.thumb{{border:1px solid var(--line);border-radius:12px;padding:6px;background:#fff}}
.thumb img{{width:100%;height:auto;display:block;border-radius:8px}}
.center{{text-align:center}}
.small{{font-size:.92rem}}
.backline{{margin:6px 0 0;}}
</style>
</head>
<body>
<header>
  <h1>MBE3 Runs</h1>
  <div class="muted">Auto-generated at {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</div>
  <div class="backline"><a href="{PROJECTS_URL}" style="color:#fff;text-decoration:underline;">Back to Projects</a></div>
  <nav>
    <a href="{MAIN_SITE}/index.html">About</a>
    <a href="{MAIN_SITE}/interests.html">Interests</a>
    <a href="{MAIN_SITE}/projects.html"><b>Projects</b></a>
    <a href="{MAIN_SITE}/coursework.html">Coursework</a>
    <a href="{MAIN_SITE}/contact.html">Contact</a>
  </nav>
</header>
"""

def list_runs():
    runs = []
    if not os.path.isdir(DATA_DIR):
        return runs
    for name in sorted(os.listdir(DATA_DIR)):
        run_dir = os.path.join(DATA_DIR, name)
        if not os.path.isdir(run_dir):
            continue
        files = sorted(os.listdir(run_dir))
        imgs = [f for f in files if f.lower().endswith(".png")]
        downloads = [f for f in files if f.lower().endswith((".csv",".txt",".json",".yaml",".yml"))]
        runs.append((name, run_dir, imgs, downloads))
    return runs

def build_html():
    header = load_site_header()
    runs = list_runs()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html = [header, '<main class="container">']
    html.append('<section class="card"><div class="small muted">Latest runs appear first. Click CSV/TXT to download; images preview below.</div></section>')

    if not runs:
        html.append('<section class="card"><div class="muted">No runs found.</div></section>')
    else:
        # 最新的放前面
        for name, run_dir, imgs, dl in reversed(runs):
            html.append('<section class="card">')
            html.append(f'<h2>{name}</h2>')

            # 下载区
            if dl:
                html.append('<div style="margin:8px 0 14px;">')
                for f in dl:
                    rel = f"data/{quote(name)}/{quote(f)}"
                    html.append(f'<a class="btn" href="{rel}">{f}</a>')
                html.append('</div>')

            # 图片网格
            if imgs:
                html.append('<div class="grid">')
                for f in imgs:
                    rel = f"data/{quote(name)}/{quote(f)}"
                    html.append('<div class="thumb">')
                    html.append(f'<img src="{rel}" alt="{f}" loading="lazy" />')
                    html.append('<div class="small muted" style="margin-top:6px;">')
                    html.append(f"{f}")
                    html.append('</div></div>')
                html.append('</div>')
            else:
                html.append('<div class="muted">No PNG figures in this run.</div>')

            html.append('</section>')

    html.append(f'<div class="center muted" style="margin:24px 0;">Last updated: {now_str}</div>')
    html.append('</main></body></html>')
    return "\n".join(html)

def main():
    html = build_html()
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[mbe3-controller] Wrote {OUT_HTML}")

if __name__ == "__main__":
    main()
