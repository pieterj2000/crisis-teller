#!/usr/bin/env python3
import sys
import sqlite3
from pathlib import Path
from sentence_transformers import SentenceTransformer
import torch

def main():
    print("start script")
    print("Cuda available: ", torch.cuda.is_available())

    markdown_dir = Path("data/markdown")
    
    if not markdown_dir.exists():
        print("Error: data/markdown directory not found.")
        return

    args = sys.argv[1:]
    force = False
    if "-f" in args:
        force = True
        args = [arg for arg in args if arg != "-f"]

    if not args:
        source_files = sorted(list(markdown_dir.glob("*")))
        
        if not source_files:
            print("No files found to embed.")
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

    model_name = "clips/e5-base-trm-nl"
    print(f"Loading SentenceTransformer model for {model_name}...")
    try:
        if torch.cuda.is_available():
            model = SentenceTransformer(model_name)
        else:
            model = SentenceTransformer(model_name, model_kwargs={"dtype": torch.float32})
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    db_path = Path("data/embeddings.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{model_name}" (
                id INTEGER PRIMARY KEY,
                embedding BLOB
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error initializing SQLite database: {e}")
        return
    
    batch_size = 1000
    success_count = 0

    print(f"Processing {len(source_files)} source files in batches of up to {batch_size}...")

    for i in range(0, len(source_files), batch_size):
        batch_files = source_files[i:i + batch_size]
        
        batch_to_process = []
        batch_ids = []
        batch_contents = []

        for src_path in batch_files:
            if not src_path.is_file():
                print(f"Warning: {src_path} is not a file.")
                continue

            try:
                article_id = int(src_path.stem)
            except ValueError:
                print(f"Warning: Filename {src_path.name} does not have a valid integer ID.")
                continue

            if not force:
                cursor.execute(f'SELECT 1 FROM "{model_name}" WHERE id = ?', (article_id,))
                if cursor.fetchone() is not None:
                    print(f"Skipped {src_path}, embedding for ID {article_id} already exists in database")
                    continue

            try:
                with open(src_path, "rt", encoding="utf-8") as f:
                    content = f.read()
                batch_to_process.append(src_path)
                batch_ids.append(article_id)
                batch_contents.append(content)
            except Exception as e:
                print(f"Error reading {src_path}: {e}")

        if not batch_contents:
            continue

        print(f"Encoding batch of {len(batch_contents)} documents (items {i+1} to {i+len(batch_contents)})...")
        try:
            embeddings = model.encode_document(batch_contents, batch_size=128)
            print("Storing batch")
            for article_id, embedding, src_path in zip(batch_ids, embeddings, batch_to_process):
                embedding_blob = embedding.tobytes()
                cursor.execute(f'''
                    INSERT OR REPLACE INTO "{model_name}" (id, embedding)
                    VALUES (?, ?)
                ''', (article_id, embedding_blob))
                print(f"Embedded ID {article_id}: {src_path} -> table '{model_name}' (shape {embedding.shape})")
                success_count += 1
            conn.commit()
            #from time import sleep
            #sleep(5)
            #print("oke")
            
        except Exception as e:
            print(f"Error processing batch starting at index {i}: {e}")

    conn.close()
    print(f"\nSuccessfully smurfed (embedded) {success_count} files into {db_path} (table: {model_name}).")

if __name__ == "__main__":
    main()
