import datetime
import itertools
import os
import re
import shutil
from pathlib import Path

from app.domain import MoveResult, MoveAction


def strip_trailing_number_groups(base: str, times: int = 2) -> str:
    # Remove trailing groups like " 1" or "_1" or "-1" up to `times` occurrences
    for _ in range(times):
        new = re.sub(r"[\s_-]*\d+$", "", base)
        if new == base:
            break
        base = new
    return base


def two_sides(files: list[str], dirpath: Path, apply_changes: bool) -> MoveResult:
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
        return MoveResult(0, 0, messages=["No files to rename"])

    total_files = len(files_ordered)
    if total_files < 10:
        padding = 1
    elif total_files < 100:
        padding = 2
    elif total_files < 1000:
        padding = 3
    else:
        padding = 4

    renames: list[MoveAction] = []
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

        padded_i = str(i).zfill(padding)
        # remove up to two trailing numeric groups separated by space/_/-
        base = strip_trailing_number_groups(base, times=2)
        # produce new name
        if ext:
            newname = f"{base}_{padded_i}.{ext}"
        else:
            newname = f"{base}_{padded_i}"
        i += 1

        dst = os.path.join(dirpath, newname)
        if os.path.exists(dst):
            print(f"Error: destination file already exists: {dst}")
            return MoveResult(1, messages=[f"Destination file already exists: {dst}"])

        # Print the command (dry-run). If --apply is set, actually move.
        # Use a verbose-like output similar to `mv -v -- src dst`
        src_quoted = f'{f}'
        dst_quoted = f'{dst}'
        renames.append(MoveAction(src_quoted, dst_quoted))

    destinations = [rename.new_path for rename in renames]
    assert len(destinations) == len(set(destinations)), f"Duplicate destination paths found: {destinations}"

    result = MoveResult(0, 0)
    for rename in renames:
        if not apply_changes:
            result.messages.append(f"Would rename: {rename.old_path} to {rename.new_path}")
        else:
            if rename.old_path == rename.new_path:
                result.messages.append(f"Error: cannot a file to itself rename of {rename.old_path} to {rename.new_path}")
                return MoveResult(1, result.processed_files, messages=result.messages)
            try:
                shutil.move(rename.old_path, rename.new_path)
                result.renames.append(rename)
                result.messages.append(f"Renamed: {rename.old_path} -> {rename.new_path}")
            except Exception as e:
                result.messages.append(f"Failed to rename {rename.old_path} -> {rename.new_path}: {e}")
                return MoveResult(1, result.processed_files, messages=result.messages)
        result.processed_files += 1


    result.messages.append(f"Total files renamed: {len(renames)}")
    result.messages.append(f"Success.")
    return result
