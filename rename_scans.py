#!/usr/bin/env python3
"""
Rename scanned files for two-sided scans.

Usage: rename_scans.py --mode MODE [--apply] <folder-or-file>
--mode=two_sides    rename files of a two-sided scan as 01.ext, 02.ext... This depends on the macOS scanner: first file has no number suffix, then 1,2..., then 8 1, 8 2, 8 3, etc. Where 8 is the last page of the previous scan.

Behavior mirrors the original shell script:
- Creates a lightweight git snapshot in the target directory (init/add/commit) but ignores errors.
- By default, it prints the mv commands (dry-run). Use --apply to actually rename.
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

from app.domain import MoveResult
from app.mode_two_sides import two_sides


def natural_key(s: str) -> list[int | str]:
    """Split string into list of strings and ints for natural/version sorting."""
    parts = re.split(r'(\d+)', s)
    key: list[int | str] = []
    for p in parts:
        if p.isdigit():
            key.append(int(p))
        else:
            key.append(p.lower())
    return key


def find_files_in_dir(dirpath: str) -> list[str]:
    # List regular files in dir (no recursion)
    entries: list[str] = []
    with os.scandir(dirpath) as it:
        for ent in it:
            if ent.is_file():
                entries.append(ent.path)
    # sort by version/natural order of basename
    entries.sort(key=lambda p: natural_key(os.path.basename(p)))
    return entries


def run_git_snapshot(dirpath: str, msg: str) -> None:
    # Try to create a minimal snapshot similar to the shell script; ignore failures
    result = subprocess.run(["git", "init", "."], cwd=dirpath, check=True)
    assert result.returncode == 0, f"git init failed"
    result = subprocess.run(["git", "add", "-f", "."], cwd=dirpath)
    if result.returncode == 0:
        pass
    elif result.returncode == 1:
        print("No new files to commit, skipping git add")
    else:
        print(f"Warning: git add failed")
    result = subprocess.run(["git", "commit", "--allow-empty", "-am", msg], cwd=dirpath, check=True)
    assert result.returncode == 0, f"git commit failed"


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Rename scanned files for two-sided scans")
    parser.add_argument("--mode", default="", help="mode to run; supported", required=True, choices=["two_sides"])
    parser.add_argument("--apply", action="store_true", help="perform the renames instead of printing them (dry-run)")
    parser.add_argument("target", help="file or directory to process")
    args = parser.parse_args(argv)

    mode = args.mode
    target = args.target
    apply_changes = args.apply

    if not target:
        print("Error: target is required")
        parser.format_usage()
        return 2

    if not os.path.exists(target):
        print(f"Error: target is not a file or directory: {target}")
        return 2

    if os.path.isfile(target):
        dirpath = os.path.dirname(os.path.abspath(target)) or "."
        files = [os.path.abspath(target)]
    else:
        dirpath = os.path.abspath(target)
        files = find_files_in_dir(dirpath)

    # Exclude files if they belong to an array
    excluded_files = [".DS_Store", ".gitignore", "Thumbs.db"]
    files = [f for f in files if os.path.basename(f) not in excluded_files]

    # Remove trailing slash
    dirpath = dirpath.rstrip("/")
    dir = Path(dirpath)

    date_of_operation = now()
    msg = f"initial commit: before rename of {date_of_operation}"
    run_git_snapshot(dirpath, msg)
    if mode == "two_sides":
        result = two_sides(files, dir, apply_changes)
    else:
        result = MoveResult(1, 0, messages=["unknown mode"])

    for message in result.messages:
        print(message)

    if result.success:
        assert result.processed_files == len(files), f"Processed {result.processed_files} files, expected {len(files)}"
        msg = f"Follow up commit: after rename of {date_of_operation}"
        run_git_snapshot(dirpath, msg)
    return result.returncode


def now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


if __name__ == '__main__':
    sys.exit(main())
