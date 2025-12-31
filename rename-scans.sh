#!/usr/bin/env bash
set -euo pipefail

date_now=$(date +"%Y-%m-%d_%H:%M:%S")

git init . || true
git add -f . || true
git commit -am "initial commit: before rename of ${date_now}" || true

# Default values
mode=""

usage() {
  cat <<-USAGE
Usage: $0 [--mode=MODE] <folder-or-file>
  --mode=two-sides    rename files of a two-sided scan as 01.ext, 02.ext... This depeds on the macOS scanner: first file has no number suffix, then 1,2..., then 8 1, 8 2, 8 3, etc. Where 8 is the last page of the previous scan.
USAGE
}

# --- moved parsing to function ----------------------------------------------
parse_args() {
  # Parse option --mode=VALUE or --mode VALUE
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --mode=*)
        mode="${1#--mode=}"
        shift
        ;;
      --mode)
        if [[ $# -lt 2 ]]; then
          echo "Missing value for --mode"
          usage
          exit 1
        fi
        mode="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        break
        ;;
    esac
  done

  if [[ $# -ne 1 ]]; then
    echo "Error: exactly one positional argument required"
    usage
    exit 1
  fi

  target="$1"
}
# ---------------------------------------------------------------------------

# Call the parser with all script args
parse_args "$@"

if [[ -f "$target" ]]; then
  dir=$(dirname -- "$target")
  # single file mode
  files=( "$target" )
elif [[ -d "$target" ]]; then
  dir="$target"
  # gather regular files in directory (sorted naturally: 1,2,3,...10,11,...)
  # Use null-delimited streams and version sort so numeric parts sort as expected.
  # Use a portable while-read loop to populate the array (avoids mapfile dependency)
  files=()
  while IFS= read -r -d '' f; do
    files+=("$f")
  done < <(find "$dir" -maxdepth 1 -type f -print0 | sort -z -V)
else
  echo "Error: target is not a file or directory: $target"
  exit 1
fi

# Remove trailing slash from dir if present
dir="${dir%/}"

# --- new: group by trailing numeric parts (0, then 1, then 2) ---------------
# Classify basenames: try 2 trailing numbers first, then 1, else 0.
files0=( "" )
files1=( "" )
files2=( "" )
for f in "${files[@]}"; do
  [[ -z "$f" ]] && continue
  filename=$(basename -- "$f")
  base="${filename%.*}"
  echo $base
  if [[ "$base" =~ ^(.+)[\ _-]+([0-9]+)[\ _-]+([0-9]+)$ ]]; then
    files2+=("$f")
  elif [[ "$base" =~ ^(.+)[\ _-]+([0-9]+)$ ]]; then
    files1+=("$f")
  else
    files0+=("$f")
  fi
done

echo "Files with no trailing number: ${#files0[@]}"
echo "Files with one trailing number: ${#files1[@]}"
echo "Files with two trailing numbers: ${#files2[@]}"

# Reassemble in the requested order: 0-number, then 1-number, then 2-number
# Append each group only if it has elements (avoid creating empty "" entries).

files=()
for f in "${files0[@]}"; do
  [[ -n "$f" ]] && files+=("$f")
done

for f in "${files1[@]}"; do
  [[ -n "$f" ]] && files+=("$f")
done

for f in "${files2[@]}"; do
  [[ -n "$f" ]] && files+=("$f")
done

# ---------------------------------------------------------------------------

if [[ ${#files[@]} -eq 0 ]]; then
  echo "No files to rename in $dir"
  exit 0
fi



i=1

for f in "${files[@]}"; do
  # skip if path empty (safety)
  [[ -z "$f" ]] && continue
  filename=$(basename -- "$f")
  extension="${filename##*.}"
  base="${filename%.*}"
  base="${base//[0-9 ]*$//}"  # remove trailing numbers and spaces
#  base="${base// /_}"  # replace spaces with underscores

  if [[ "$mode" == "two-sides" ]]; then
    # Calculate padding width based on total number of files
    total_files=${#files[@]}
    if [[ $total_files -lt 10 ]]; then
      padding=1
    elif [[ $total_files -lt 100 ]]; then
      padding=2
    elif [[ $total_files -lt 1000 ]]; then
      padding=3
    else
      padding=4
    fi
    
    # Pad the number with leading zeros
    padded_i=$(printf "%0${padding}d" $i)
    # Remove trailing 0, 1, or 2 numbers from base
    base=$(echo "$base" | sed -E 's/[[:space:]_-]*[0-9]*$//')
    base=$(echo "$base" | sed -E 's/[[:space:]_-]*[0-9]*$//')
    newname="${base}_${padded_i}.${extension}"
    ((i++))
  else
    echo "mode is unsupported"
    exit 1
  fi

  if [[ -e "$dir/$newname" ]]; then
    echo "Error: destination file already exists: $dir/$newname"
    exit 1
  fi
  echo mv -v -- "$f" "$dir/$newname"
  #mv -v -- "$f" "$dir/$newname"
done
