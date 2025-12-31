#!/usr/bin/env python3
"""
Rename scanned files for two-sided scans.

Usage: rename_scans.py [--mode MODE] [--apply] <folder-or-file>
--mode=two-sides    rename files of a two-sided scan as 01.ext, 02.ext... This depends on the macOS scanner: first file has no number suffix, then 1,2..., then 8 1, 8 2, 8 3, etc. Where 8 is the last page of the previous scan.

Behavior mirrors the original shell script:
- Creates a lightweight git snapshot in the target directory (init/add/commit) but ignores errors.
- By default prints the mv commands (dry-run). Use --apply to actually rename.
"""
import argparse
import datetime
import itertools
import os
import re
import shutil
import subprocess
import sys


def natural_key(s: str):
    """Split string into list of strings and ints for natural/version sorting."""
    parts = re.split(r'(\d+)', s)
    key = []
    for p in parts:
        if p.isdigit():
            key.append(int(p))
        else:
            key.append(p.lower())
    return key


def find_files_in_dir(dirpath):
    # List regular files in dir (no recursion)
    entries = []
    with os.scandir(dirpath) as it:
        for ent in it:
            if ent.is_file():
                entries.append(ent.path)
    # sort by version/natural order of basename
    entries.sort(key=lambda p: natural_key(os.path.basename(p)))
    return entries


def run_git_snapshot(dirpath, date_now):
    # Try to create a minimal snapshot similar to the shell script; ignore failures
    try:
        subprocess.run(["git", "init", "."], cwd=dirpath, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "add", "-f", "."], cwd=dirpath, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        msg = f"initial commit: before rename of {date_now}"
        subprocess.run(["git", "commit", "-am", msg], cwd=dirpath, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        # best-effort only
        pass


def strip_trailing_number_groups(base: str, times: int = 2) -> str:
    # Remove trailing groups like " 1" or "_1" or "-1" up to `times` occurrences
    for _ in range(times):
        new = re.sub(r"[\s_-]*\d+$", "", base)
        if new == base:
            break
        base = new
    return base


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Rename scanned files for two-sided scans")
    parser.add_argument("--mode", default="", help="mode to run; supported: two-sides", required=True, choices=["two-sides"])
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

    # Remove trailing slash
    dirpath = dirpath.rstrip("/")

    # Group by trailing numeric parts
    files0 = []
    files1 = []
    files2 = []

    for f in files:
        if not f:
            continue
        filename = os.path.basename(f)
        base, _ = os.path.splitext(filename)
        if re.match(r"^(.+)[ _-]+(\d+)[ _-]+(\d+)$", base):
            files2.append(f)
        elif re.match(r"^(.+)[ _-]+(\d+)$", base):
            files1.append(f)
        else:
            files0.append(f)

    print(f"Files with no trailing number: {len(files0)}")
    print(f"Files with one trailing number: {len(files1)}")
    print(f"Files with two trailing numbers: {len(files2)}")

    files_ordered = []
    files_ordered.extend(files0)
    files2.reverse()
    # Zip files2 and files1 together, interleaving them
    for f2, f1 in itertools.zip_longest(files2, files1, fillvalue=None):
        if f2 is not None:
            files_ordered.append(f2)
        if f1 is not None:
            files_ordered.append(f1)

    if len(files_ordered) == 0:
        print(f"No files to rename in {dirpath}")
        return 0

    date_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    # attempt git snapshot (best-effort)
    run_git_snapshot(dirpath, date_now)

    total_files = len(files_ordered)
    if total_files < 10:
        padding = 1
    elif total_files < 100:
        padding = 2
    elif total_files < 1000:
        padding = 3
    else:
        padding = 4

    i = 1
    for f in files_ordered:
        if not f:
            continue
        filename = os.path.basename(f)
        name_no_ext, ext = os.path.splitext(filename)
        ext = ext[1:] if ext.startswith('.') else ext

        # remove trailing numbers and spaces (like the shell script)
        base = name_no_ext
        base = re.sub(r"[0-9 ]*$", "", base)

        if mode == "two-sides":
            padded_i = str(i).zfill(padding)
            # remove up to two trailing numeric groups separated by space/_/-
            base = strip_trailing_number_groups(base, times=2)
            # produce new name
            if ext:
                newname = f"{base}_{padded_i}.{ext}"
            else:
                newname = f"{base}_{padded_i}"
            i += 1
        else:
            print("mode is unsupported")
            return 1

        dst = os.path.join(dirpath, newname)
        if os.path.exists(dst):
            print(f"Error: destination file already exists: {dst}")
            return 1

        # Print the command (dry-run). If --apply is set, actually move.
        # Use a verbose-like output similar to `mv -v -- src dst`
        src_quoted = f'"{f}"'
        dst_quoted = f'"{dst}"'
        if not apply_changes:
            print(f"Would rename: {src_quoted} to {dst_quoted}")
        else:
            try:
                shutil.move(f, dst)
                print(f"Renamed: {f} -> {dst}")
            except Exception as e:
                print(f"Failed to rename {f} -> {dst}: {e}")
                return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())

