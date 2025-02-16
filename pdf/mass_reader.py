#!/usr/bin/env python3

import os
import subprocess
import pymupdf  # or `import fitz` if you prefer PyMuPDF's canonical import

INPUT_DOIS_FILE = "docs/in.txt"

def sanitize_filename(s: str) -> str:
    """
    Replace characters that are invalid on most filesystems
    (like slashes, colons, etc.) with underscores or another safe character.
    """
    return s.replace("/", "_").replace("\\", "_").replace(":", "_")


def main():
    with open(INPUT_DOIS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            doi = line.strip()
            if not doi:
                continue  # Skip empty lines

            # 1. Download the PDF via the downloader script
            subprocess.run(["python3", "zotero/downloader.py", doi])

            # 2. Construct the paths
            safe_doi = sanitize_filename(doi)
            pdf_path = os.path.join("docs", f"{safe_doi}.pdf")
            txt_path = os.path.join("docs", f"{safe_doi}.txt")

            if not os.path.isfile(pdf_path):
                print(f"Warning: No PDF found at {pdf_path} after download step.")
                continue

            # 3. Extract text from the PDF to a separate text file
            try:
                doc = pymupdf.open(pdf_path)
                with open(txt_path, "wb") as out_file:
                    for page in doc:
                        text = page.get_text().encode("utf8")
                        out_file.write(text)
                        out_file.write(bytes((12,)))  # form feed (0x0C) as page delimiter
                doc.close()
                print(f"Extracted text for DOI '{doi}' -> {txt_path}")

            except Exception as e:
                print(f"Error reading PDF {pdf_path}: {e}")


if __name__ == "__main__":
    main()
