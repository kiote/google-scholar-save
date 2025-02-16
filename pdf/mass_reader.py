#!/usr/bin/env python3

import os
import subprocess
import pymupdf  # or `import fitz` if you prefer PyMuPDF's canonical import
import re

INPUT_DOIS_FILE = "docs/in.txt"


def remove_unwanted_sections(text: str) -> str:
    """Remove 'Related Work' / 'References' sections from text."""
    related_pattern = re.compile(
        r'^(?:\d+\s*[\.\)]\s*)?(?:related\s+works?)\b.*$',
        re.IGNORECASE | re.MULTILINE
    )
    refs_pattern = re.compile(
        r'^(?:\d+\s*[\.\)]\s*)?(?:references|bibliography)\b.*$',
        re.IGNORECASE | re.MULTILINE
    )
    generic_heading = re.compile(
        r'^(?!Figure|Table)(?:\d+\s*[\.\)]\s*)?[A-Z][A-Za-z0-9\-\s\:,\&]{0,50}$',
        re.MULTILINE
    )

    cleaned_text = text

    # Remove "Related Work" section if present
    match = related_pattern.search(cleaned_text)
    if match:
        start_idx = match.start()
        next_header = generic_heading.search(cleaned_text, match.end())
        if next_header:
            end_idx = next_header.start()
        else:
            end_idx = len(cleaned_text)
        cleaned_text = cleaned_text[:start_idx] + cleaned_text[end_idx:]

    # Remove "References"/"Bibliography" section if present
    match = refs_pattern.search(cleaned_text)
    if match:
        start_idx = match.start()
        next_header = generic_heading.search(cleaned_text, match.end())
        if next_header:
            end_idx = next_header.start()
        else:
            end_idx = len(cleaned_text)
        cleaned_text = cleaned_text[:start_idx] + cleaned_text[end_idx:]

    return cleaned_text


def sanitize_filename(s: str) -> str:
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

            # 3. Extract text from the PDF to a single string
            try:
                doc = pymupdf.open(pdf_path)

                # Collect all pages in one list
                all_pages_text = []
                for page in doc:
                    # get_text() returns a string
                    page_text = page.get_text()
                    # We can optionally add a page-break marker if needed
                    all_pages_text.append(page_text)

                doc.close()

                # Join all pages into a single string
                full_text = "\n\f\n".join(all_pages_text)

                # 4. Remove unwanted sections (across *all* pages)
                cleaned_text = remove_unwanted_sections(full_text)

                # 5. Write the cleaned text to file (in binary mode, but encoding text)
                with open(txt_path, "wb") as out_file:
                    out_file.write(cleaned_text.encode("utf-8"))

                print(f"Extracted and cleaned text for DOI '{doi}' -> {txt_path}")

            except Exception as e:
                print(f"Error reading PDF {pdf_path}: {e}")


if __name__ == "__main__":
    main()
