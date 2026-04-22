import argparse
import csv
import json
import os
import sys


CONTENT_TYPE = "CONTENT"
DELETED_CONTENT_TYPE = "DELETED_CONTENT"


def collect_entries(input_dir):
    entries = []

    for filename in sorted(os.listdir(input_dir)):
        if not filename.lower().endswith(".json"):
            continue

        filepath = os.path.join(input_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: could not read '{filepath}': {e}", file=sys.stderr)
            continue

        for entry in data.get("content", []):
            row = dict(entry)
            row["fileName"] = filename
            row["operationType"] = CONTENT_TYPE
            entries.append(row)

        for entry in data.get("deletedContent", []):
            row = dict(entry)
            row["fileName"] = filename
            row["operationType"] = DELETED_CONTENT_TYPE
            entries.append(row)

    return entries


def get_fieldnames(entries):
    # Collect unique field names in insertion order (dict.fromkeys preserves order)
    all_keys = dict.fromkeys(key for entry in entries for key in entry)
    # Ensure fileName and type appear as the last two columns
    fixed_cols = {"fileName", "operationType"}
    base_cols = [k for k in all_keys if k not in fixed_cols]
    return base_cols + ["fileName", "operationType"]


def write_csv(entries, output_path):
    if not entries:
        print("No entries found. CSV will not be created.", file=sys.stderr)
        return

    fieldnames = get_fieldnames(entries)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(entries)

    print(f"Wrote {len(entries)} entries to '{output_path}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Parse JSON files and write content/deletedContent entries to a CSV file."
    )
    parser.add_argument("input_dir", help="Directory containing JSON files")
    parser.add_argument(
        "output_csv",
        nargs="?",
        default="output.csv",
        help="Path to the output CSV file (default: output.csv)",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: '{args.input_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    entries = collect_entries(args.input_dir)
    write_csv(entries, args.output_csv)


if __name__ == "__main__":
    main()
