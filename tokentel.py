#!/usr/bin/env python3
import sys
from pathlib import Path
from transformers import AutoTokenizer

def main():
    print("start script")


    markdown_dir = Path("data/markdown")
    
    if not markdown_dir.exists():
        print("Error: data/markdown directory not found.")
        return

    args = sys.argv[1:]

    if not args:
        source_files = sorted(list(markdown_dir.glob("*")))
        
        if not source_files:
            print("No files found to count tokens.")
            return
    else:
        source_files = []
        for arg in args:
            candidates = [
                markdown_dir / arg,
                markdown_dir / f"{arg}.md"
            ]

            found = False
            for c in candidates:
                if c.exists():
                    source_files.append(c)
                    found = True
                    break
            
            if not found:
                print(f"Warning: File for argument '{arg}' not found in {markdown_dir}")

    if not source_files:
        print("No valid source files to process.")
        return

    print("Loading tokenizer for pdelobelle/robbert-2026...")
    try:
        tokenizer = AutoTokenizer.from_pretrained("pdelobelle/robbert-2026", trust_remote_code=True)
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        return

    longest_file = None
    max_tokens = -1
    
    for src_path in source_files:
        if not src_path.is_file():
            raise Exception("errorr src path is niet file: " + str(src_path))
            continue

        try:
            with open(src_path, "rt", encoding="utf-8") as f:
                content = f.read()
            tokens = tokenizer.encode(content)
            count = len(tokens)
            print(f"{src_path}: {count} tokens")

            if count > max_tokens:
                max_tokens = count
                longest_file = src_path
        except Exception as e:
            print(f"Error processing {src_path}: {e}")

    if longest_file is not None:
        print(f"\nLongest file: {longest_file} with {max_tokens} tokens")

if __name__ == "__main__":
    main()
