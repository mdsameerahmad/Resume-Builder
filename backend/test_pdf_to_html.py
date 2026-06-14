import fitz
import sys
import os

def test_html_extraction(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        page = doc[i]
        html = page.get_text("html")
        with open(f"page_{i}.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved page {i} to page_{i}.html")
    doc.close()

if __name__ == "__main__":
    # Just a placeholder to see what it generates if we had a file
    print("This script requires a PDF file to run.")
