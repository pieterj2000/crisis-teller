#!/usr/bin/env python3
import sys
from pathlib import Path
import html2text

def main():
    ongzip_dir = Path("data/ongzip")
    markdown_dir = Path("data/markdown")
    markdown_dir.mkdir(parents=True, exist_ok=True)

    args = sys.argv[1:]
    skip_existing = not args

    if not args:
        # Convert all files in data/ongzip/
        source_files = list(ongzip_dir.glob("*"))
        if not source_files:
            print(f"No files found in {ongzip_dir}")
            return
    else:
        source_files = []
        for arg in args:                
            # Try matching in ongzip_dir with various suffixes
            candidates = [
                ongzip_dir / arg,
                ongzip_dir / f"{arg}.html",
            ]

            found = False
            for c in candidates:
                if c.exists():
                    source_files.append(c)
                    found = True
                    break
            
            if not found:
                print(f"Warning: File for argument '{arg}' not found in {ongzip_dir}")

    if not source_files:
        print("No valid source files to convert.")
        return

    for src_path in source_files:
        if not src_path.is_file():
            raise Exception("errorr src path is niet file: " + str(src_path))
            continue
        
        # Determine output path (e.g. data/ongzip/113755.html -> data/markdown/113755.md)
        filename = src_path.name
        dest_filename = filename[:-5] + ".md"
        dest_path = markdown_dir / dest_filename

        if skip_existing and dest_path.exists():
            print(f"Skipped {src_path}, output {dest_path} already exists")
            continue

        try:
            with open(src_path, "rt", encoding="utf-8") as f_in:
                html_content = f_in.read()
            markdown_content = html2text.html2text(html_content)
            with open(dest_path, "wt", encoding="utf-8") as f_out:
                f_out.write(markdown_content)
            print(f"Converted: {src_path} -> {dest_path}")
        except Exception as e:
            raise Exception(f"Error converting {src_path}: {e}")

if __name__ == "__main__":
    main()
