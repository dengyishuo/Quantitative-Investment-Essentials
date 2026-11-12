#!/usr/bin/env python3
"""Build the multi-page static site used by GitHub Pages."""

from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path

from build_book import BOOK_SLUG, ROOT, build, chapter_paths


SITE_DIR = ROOT / "dist" / "site"
ASSET_SOURCE = ROOT / "script" / "assets"


def chapter_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def render_markdown(path: Path) -> str:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("Pandoc is required. Install it from https://pandoc.org/")

    result = subprocess.run(
        [
            pandoc,
            "--from=markdown+tex_math_dollars",
            "--to=html5",
            "--mathml",
            "--quiet",
            str(path),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def navigation(chapters: list[tuple[Path, str]], current: int | None) -> str:
    prefix = "" if current is not None else "chapters/"
    links: list[str] = []
    for index, (path, title) in enumerate(chapters):
        active = ' class="active" aria-current="page"' if index == current else ""
        links.append(
            f'<li><a{active} href="{prefix}{path.stem}.html">'
            f"{html.escape(title)}</a></li>"
        )
    return "\n".join(links)


def page_shell(
    *,
    title: str,
    body: str,
    chapters: list[tuple[Path, str]],
    current: int | None,
    previous_link: str = "",
    next_link: str = "",
) -> str:
    nested = current is not None
    root_prefix = "../" if nested else ""
    home_url = "../index.html" if nested else "index.html"
    nav = navigation(chapters, current)
    pager = ""
    if previous_link or next_link:
        pager = (
            '<nav class="pager" aria-label="内容翻页">'
            f'<div class="pager-prev">{previous_link}</div>'
            f'<div class="pager-next">{next_link}</div>'
            "</nav>"
        )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="量化投资精要，揖光尘著">
  <title>{html.escape(title)} · 量化投资精要</title>
  <link rel="stylesheet" href="{root_prefix}assets/book.css">
</head>
<body>
  <button class="menu-button" type="button" aria-label="打开目录" aria-expanded="false">☰</button>
  <aside class="sidebar" id="sidebar">
    <a class="brand" href="{home_url}">量化投资精要</a>
    <p class="author">揖光尘</p>
    <nav aria-label="全书目录"><ol>{nav}</ol></nav>
  </aside>
  <div class="backdrop" hidden></div>
  <main class="content">
    <article>{body}</article>
    {pager}
    <footer>《量化投资精要》 · 揖光尘 · MIT License</footer>
  </main>
  <script src="{root_prefix}assets/book.js"></script>
</body>
</html>
"""


def chapter_pager(
    chapters: list[tuple[Path, str]], index: int
) -> tuple[str, str]:
    previous_link = ""
    next_link = ""
    if index > 0:
        path, title = chapters[index - 1]
        previous_link = (
            f'<a rel="prev" href="{path.stem}.html">← {html.escape(title)}</a>'
        )
    if index + 1 < len(chapters):
        path, title = chapters[index + 1]
        next_link = (
            f'<a rel="next" href="{path.stem}.html">{html.escape(title)} →</a>'
        )
    return previous_link, next_link


def build_index(chapters: list[tuple[Path, str]]) -> str:
    chapter_cards = "\n".join(
        f'<li><a href="chapters/{path.stem}.html">{html.escape(title)}</a></li>'
        for path, title in chapters
    )
    return f"""
<header class="hero">
  <p class="eyebrow">QUANTITATIVE INVESTMENT ESSENTIALS</p>
  <h1>量化投资精要</h1>
  <p class="hero-author">揖光尘 著</p>
  <p class="lead">从金融理论、资产与数据出发，系统介绍多因子、机器学习、套利、资产配置、风险管理、交易执行，以及LLM、Agent与Vibe Coding在量化研究中的应用。</p>
  <div class="hero-actions">
    <a class="primary" href="chapters/{chapters[0][0].stem}.html">开始阅读</a>
    <a href="downloads/{BOOK_SLUG}.epub" download>下载 EPUB</a>
  </div>
</header>
<section class="home-section">
  <h2>全书目录</h2>
  <ul class="chapter-grid">{chapter_cards}</ul>
</section>
<section class="home-section note">
  <h2>阅读说明</h2>
  <p>本书用于知识学习和研究交流，不构成投资建议、交易建议或收益承诺。历史结果不代表未来表现。</p>
</section>
"""


def redirect_page(target: str) -> str:
    """Return a small compatibility redirect for a renamed book page."""
    escaped_target = html.escape(target, quote=True)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={escaped_target}">
  <link rel="canonical" href="{escaped_target}">
  <title>页面已移动 · 量化投资精要</title>
</head>
<body><p>页面已移动至 <a href="{escaped_target}">{escaped_target}</a>。</p></body>
</html>
"""


def main() -> None:
    paths = chapter_paths()
    chapters = [(path, chapter_title(path)) for path in paths]

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    (SITE_DIR / "chapters").mkdir(parents=True)
    (SITE_DIR / "assets").mkdir()
    (SITE_DIR / "downloads").mkdir()

    shutil.copy2(ASSET_SOURCE / "book.css", SITE_DIR / "assets" / "book.css")
    shutil.copy2(ASSET_SOURCE / "book.js", SITE_DIR / "assets" / "book.js")
    shutil.copytree(ROOT / "images", SITE_DIR / "images")
    shutil.copy2(ROOT / "LICENSE", SITE_DIR / "LICENSE.txt")
    (SITE_DIR / ".nojekyll").touch()

    epub = build("epub", ROOT / "dist", paths)
    shutil.copy2(epub, SITE_DIR / "downloads" / epub.name)

    index_body = build_index(chapters)
    (SITE_DIR / "index.html").write_text(
        page_shell(
            title="首页", body=index_body, chapters=chapters, current=None
        ),
        encoding="utf-8",
    )

    for index, (path, title) in enumerate(chapters):
        previous_link, next_link = chapter_pager(chapters, index)
        page = page_shell(
            title=title,
            body=render_markdown(path),
            chapters=chapters,
            current=index,
            previous_link=previous_link,
            next_link=next_link,
        )
        (SITE_DIR / "chapters" / f"{path.stem}.html").write_text(
            page, encoding="utf-8"
        )

    legacy_pages = {
        "00-preface.html": "preface.html",
        "33-references.html": "references.html",
    }
    for old_name, target in legacy_pages.items():
        (SITE_DIR / "chapters" / old_name).write_text(
            redirect_page(target), encoding="utf-8"
        )

    print(f"Created GitHub Pages site at {SITE_DIR}")
    print(f"Generated {len(chapters)} book pages and EPUB download")


if __name__ == "__main__":
    main()
