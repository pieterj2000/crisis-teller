#!/usr/bin/env python3
import sys
import gzip
from pathlib import Path

def main():
    rauw_dir = Path("data/rauw")
    ongzip_dir = Path("data/ongzip")
    ongzip_dir.mkdir(parents=True, exist_ok=True)

    args = sys.argv[1:]
    skip_existing = not args

    if not args:
        # Decompress all files in data/rauw/
        source_files = list(rauw_dir.glob("*"))
        if not source_files:
            print(f"No files found in {rauw_dir}")
            return
    else:
        source_files = []
        for arg in args:                
            # Try matching in rauw_dir with various suffixes
            candidates = [
                rauw_dir / arg,
                rauw_dir / f"{arg}.gzip",
                rauw_dir / f"{arg}.html.gzip",
            ]

            found = False
            for c in candidates:
                if c.exists():
                    source_files.append(c)
                    found = True
                    break
            
            if not found:
                print(f"Warning: File for argument '{arg}' not found in {rauw_dir}", file=sys.stderr)

    if not source_files:
        print("No valid source files to decompress.")
        return

    for src_path in source_files:
        if not src_path.is_file():
            raise Exception("errorr src path is niet file: " + src_path)
            continue
        
        # Determine output path (e.g. data/rauw/113755.html.gzip -> data/ongzip/113755.html)
        filename = src_path.name
        dest_filename = filename[:-5]
        dest_path = ongzip_dir / dest_filename

        if skip_existing and dest_path.exists():
            print(f"Skipped {src_path}, output {dest_path} already exists")
            continue

        try:
            with gzip.open(src_path, "rb") as f_in:
                with open(dest_path, "wb") as f_out:
                    f_out.write(f_in.read())
            print(f"Decompressed: {src_path} -> {dest_path}")
        except Exception as e:
            raise Exception(f"Error decompressing {src_path}: {e}")

if __name__ == "__main__":
    main()
