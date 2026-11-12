#!/usr/bin/env python3
"""Build HTML and EPUB editions of Quantitative Investment Essentials."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
DEFAULT_OUTPUT = ROOT / "dist"
BOOK_SLUG = "quantitative-investment-essentials"

BOOK_ENTRY_LINK = re.compile(
    r"^\s*-\s+\[[^]]+\]\(<(markdown/[^>]+\.md)>\)\s*$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--format",
        action="append",
        choices=("html", "epub"),
        dest="formats",
        help="Output format; repeat to build more than one. Defaults to both.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory. Defaults to dist/.",
    )
    return parser.parse_args()


def chapter_paths() -> list[Path]:
    chapters: list[Path] = []
    for line in README.read_text(encoding="utf-8").splitlines():
        match = BOOK_ENTRY_LINK.match(line)
        if match:
            chapters.append(ROOT / match.group(1))

    if not chapters:
        raise RuntimeError("No book-entry links were found in README.md")
    if len(chapters) != len(set(chapters)):
        raise RuntimeError("README.md contains duplicate book-entry links")

    missing = [path for path in chapters if not path.is_file()]
    if missing:
        missing_list = "\n".join(f"- {path.relative_to(ROOT)}" for path in missing)
        raise FileNotFoundError(f"Missing book files:\n{missing_list}")
    return chapters


def pandoc_base(chapters: list[Path]) -> list[str]:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("Pandoc is required. Install it from https://pandoc.org/")

    resource_path = f"{ROOT / 'markdown'}:{ROOT}"
    return [
        pandoc,
        "--from=markdown+tex_math_dollars",
        "--standalone",
        "--quiet",
        "--toc",
        "--toc-depth=3",
        "--metadata=title:量化投资精要",
        "--metadata=author:揖光尘",
        "--metadata=lang:zh-CN",
        "--metadata=rights:MIT",
        f"--resource-path={resource_path}",
        *(str(path) for path in chapters),
    ]


def build(fmt: str, output_dir: Path, chapters: list[Path]) -> Path:
    extension = "html" if fmt == "html" else "epub"
    output = output_dir / f"{BOOK_SLUG}.{extension}"
    command = pandoc_base(chapters)

    if fmt == "html":
        command.extend(("--to=html5", "--embed-resources"))
    else:
        command.append("--to=epub3")
    command.extend(("--output", str(output)))

    print(f"Building {fmt.upper()}: {output.relative_to(ROOT)}")
    subprocess.run(command, cwd=ROOT, check=True)
    return output


def main() -> None:
    args = parse_args()
    formats = args.formats or ["html", "epub"]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    chapters = chapter_paths()

    print(f"Found {len(chapters)} book entries in README.md")
    outputs = [build(fmt, output_dir, chapters) for fmt in formats]
    for output in outputs:
        size_mb = output.stat().st_size / (1024 * 1024)
        print(f"Created {output} ({size_mb:.2f} MiB)")


if __name__ == "__main__":
    main()

