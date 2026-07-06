#!/usr/bin/env python3
"""
New Hope Lutheran Church livestream viewer updater.

Accept a pasted YouTube URL, extract the 11-character video ID,
update index.html in C:\\ChurchAutomation\\live-stream-viewer,
and optionally commit/push the change to GitHub.

Usage examples:

  python update_viewer_video_id.py
  python update_viewer_video_id.py "https://www.youtube.com/watch?v=abc123XYZ45"
  python update_viewer_video_id.py "https://youtu.be/abc123XYZ45" --commit
  python update_viewer_video_id.py "https://www.youtube.com/live/abc123XYZ45?feature=share" --commit --push
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DEFAULT_PROJECT_DIR = Path(r"C:\ChurchAutomation\live-stream-viewer")
INDEX_FILE_NAME = "index.html"
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(text: str) -> str:
    """Extract an 11-character YouTube video ID from a URL or raw pasted ID."""
    value = text.strip()

    if VIDEO_ID_RE.fullmatch(value):
        return value

    parsed = urlparse(value)

    # Standard watch URL: https://www.youtube.com/watch?v=VIDEO_ID
    query = parse_qs(parsed.query)
    if "v" in query and query["v"]:
        candidate = query["v"][0]
        if VIDEO_ID_RE.fullmatch(candidate):
            return candidate

    # Short URL: https://youtu.be/VIDEO_ID
    if parsed.netloc.lower().endswith("youtu.be"):
        candidate = parsed.path.strip("/").split("/")[0]
        if VIDEO_ID_RE.fullmatch(candidate):
            return candidate

    # Live / embed / shorts URL:
    # https://www.youtube.com/live/VIDEO_ID?feature=share
    # https://www.youtube.com/embed/VIDEO_ID
    path_parts = [part for part in parsed.path.split("/") if part]
    for marker in ("live", "embed", "shorts"):
        if marker in path_parts:
            idx = path_parts.index(marker)
            if idx + 1 < len(path_parts):
                candidate = path_parts[idx + 1]
                if VIDEO_ID_RE.fullmatch(candidate):
                    return candidate

    # Last-resort search for a standalone 11-character ID in pasted text.
    match = re.search(r"(?<![A-Za-z0-9_-])([A-Za-z0-9_-]{11})(?![A-Za-z0-9_-])", value)
    if match:
        return match.group(1)

    raise ValueError(
        "Could not find a valid 11-character YouTube video ID. "
        "Paste a normal YouTube watch URL, live URL, youtu.be URL, or the raw video ID."
    )


def update_index_html(index_path: Path, video_id: str) -> None:
    """Update VIDEO_ID inside the marked block in index.html."""
    html = index_path.read_text(encoding="utf-8")

    pattern = re.compile(
        r'(// START_VIDEO_ID\s*const\s+VIDEO_ID\s*=\s*")[^"]*(";\s*// END_VIDEO_ID)',
        re.DOTALL,
    )

    if not pattern.search(html):
        raise RuntimeError(
            "Could not find the START_VIDEO_ID / END_VIDEO_ID marker block in index.html. "
            "Use the updated index.html template that includes those markers."
        )

    updated = pattern.sub(rf"\g<1>{video_id}\2", html, count=1)
    index_path.write_text(updated, encoding="utf-8")


def run_git(project_dir: Path, args: list[str]) -> None:
    """Run a git command in the project directory."""
    subprocess.run(["git", *args], cwd=project_dir, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update the New Hope Lutheran Church Cloudflare viewer with a new YouTube video ID."
    )
    parser.add_argument(
        "youtube_url",
        nargs="?",
        help="YouTube URL or raw 11-character video ID. If omitted, you will be prompted.",
    )
    parser.add_argument(
        "--project-dir",
        default=str(DEFAULT_PROJECT_DIR),
        help=rf"Folder containing index.html. Default: {DEFAULT_PROJECT_DIR}",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit the index.html change to the local Git repository.",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the commit to GitHub after committing. Implies --commit.",
    )

    args = parser.parse_args()
    project_dir = Path(args.project_dir)
    index_path = project_dir / INDEX_FILE_NAME

    if not index_path.exists():
        print(f"ERROR: Could not find {index_path}", file=sys.stderr)
        return 1

    pasted = args.youtube_url or input("Paste the YouTube scheduled stream URL or video ID: ").strip()

    try:
        video_id = extract_video_id(pasted)
        update_index_html(index_path, video_id)
        print(f"Updated {index_path}")
        print(f"New VIDEO_ID: {video_id}")

        if args.push:
            args.commit = True

        if args.commit:
            run_git(project_dir, ["add", INDEX_FILE_NAME])
            run_git(project_dir, ["commit", "-m", f"Update livestream video ID to {video_id}"])
            print("Committed change to Git.")

        if args.push:
            run_git(project_dir, ["push"])
            print("Pushed change to GitHub.")

        return 0

    except subprocess.CalledProcessError as exc:
        print(f"ERROR: Git command failed: {exc}", file=sys.stderr)
        return exc.returncode or 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
