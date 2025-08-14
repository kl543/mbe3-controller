# scripts/gen_docs.py
import os
from pathlib import Path
from urllib.parse import quote
from datetime import datetime

ROOT = Path(".")
DATA_DIR = ROOT / "data"
OUT = ROOT / "index.html"

def q(p: Path | str) -> str:
    """URL-encode a relative path for href/src (保留常见安全字符)."""
    if isinstance(p, Path):
        p = p.as_posix()
    return quote(p, safe="/-._")

def h(s: str) -> str:
    """简单转义（标题里基本只会有空格和#，这里足够）"""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def section_for_run(run_dir: Path) -> str:
    rel_dir = run_dir.relative_to(ROOT).as_posix()
    title = run_dir.name  # 原文件夹名作为显示标题
    imgs = sorted(run_dir.glob("*.png"))
    docs = sorted([*run_dir.glob("*.csv"), *run_dir.glob("*.txt")])

    img_html = ""
    if imgs:
        tiles = []
        for img in imgs:
            href = q(img.relative_to(ROOT))
            cap = h(img.name)
            tiles.append(
                f"""
                <a class="tile" href="{href}" target="_blank" rel="noreferrer">
                  <img loading="lazy" src="{href}" alt="{cap}">
                  <div class="cap">{cap}</div>
                </a>
                """
            )
        img_html = f"""
        <div class="subtle">Images</div>
        <div class="grid">
          {''.join(tiles)}
        </div>
        """

    dl_html = ""
    if docs:
        items = []
        for f in docs:
            href = q(f.relative_to(ROOT))
            items.append(f'<li><a href="{href}">{h(f.name)}</a></li>')
        dl_html = f"""
        <div class="subtle">Downloads</div>
        <ul class="downloads">
          {''.join(items)}
        </ul>
        """

    if not imgs and not docs:
        empty = '<p class="muted">No plots or logs found in this run.</p>'
    else:
        empty = ""

    return f"""
    <section class="card">
      <h2>{h(title)}</h2>
      {img_html}
      {dl_html}
      {empty}
    </section>
    """

def build_page() -> str:
    runs = []
    if DATA_DIR.exists():
        # 最近的放前面
        candidates = [d for d in DATA_DIR.iterdir() if d.is_dir()]
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for d in candidates:
            runs.append(section_for_run(d))
    else:
        runs.append('<p class="muted">No data/ directory.</p>')

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>MBE3 Runs</title>
  <style>
    :root{{--ink:#111;--line:#e9e9e9;--muted:#666;--bg:#fff;--pill:#f5f5f7}}
    *{{box-sizing:border-box}} body{{margin:0;font:16px/1.6 -apple-system,system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:#fafafa}}
    header{{background:#111;color:#fff;text-align:center;padding:40px 16px}}
    header h1{{margin:0 0 6px}}
    header .sub{{opacity:.8}}
    .bar{{display:flex;gap:10px;justify-content:center;margin-top:12px}}
    .btn{{display:inline-block;padding:8px 12px;border-radius:10px;border:1px solid var(--line);background:#fff;color:var(--ink);text-decoration:none}}
    .btn:hover{{background:var(--pill)}}
    main{{max-width:1100px;margin:24px auto;padding:0 16px}}
    .note{{border:1px solid var(--line);background:#fff;border-radius:12px;padding:12px 14px;color:var(--muted);margin-bottom:16px}}
    .card{{border:1px solid var(--line);background:#fff;border-radius:16px;padding:18px;margin:18px 0}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin-top:8px}}
    .tile{{display:block;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;text-decoration:none;color:inherit}}
    .tile img{{width:100%;display:block;aspect-ratio:4/3;object-fit:cover;}}
    .tile .cap{{padding:8px 10px;font-size:13px;color:var(--muted);border-top:1px solid var(--line)}}
    .downloads{{margin:6px 0 0 18px}}
    .muted{{color:var(--muted)}}
    .subtle{{color:var(--muted);font-size:13px;margin-top:4px}}
    footer{{text-align:center;color:var(--muted);font-size:13px;margin:28px 0}}
  </style>
</head>
<body>
<header>
  <h1>MBE3 Runs</h1>
  <div class="sub">Auto-generated at {ts}</div>
  <div class="bar">
    <a class="btn" href="https://kl543.github.io/projects.html">Back to Projects</a>
    <a class="btn" href="https://github.com/kl543/mbe3-controller" target="_blank" rel="noreferrer">Repo</a>
  </div>
</header>

<main>
  <div class="note">Latest runs appear first. Click an image to view the full PNG; CSV/TXT are available in Downloads.</div>
  {''.join(runs)}
</main>

<footer>© {datetime.utcnow().year} Kaiming Liu</footer>
</body>
</html>
"""

def main():
    html = build_page()
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT.resolve()}")

if __name__ == "__main__":
    main()
