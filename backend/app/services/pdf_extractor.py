import fitz  # PyMuPDF
import pdfplumber
from typing import Dict, Any, Tuple, List
from loguru import logger
import io

class PDFExtractor:
    def __init__(self):
        pass

    async def extract(self, file_content: bytes) -> Dict[str, Any]:
        """
        Extracts text, metadata, and links from PDF content.
        """
        raw_text = ""
        metadata = {
            "page_count": 0,
            "file_type": "pdf",
            "page_dimensions": []
        }
        links = []

        try:
            # 1. Use PyMuPDF for text and link extraction
            doc = fitz.open(stream=file_content, filetype="pdf")
            metadata["page_count"] = len(doc)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                raw_text += page.get_text() + "\n"
                
                # Extract hyperlinks
                for link in page.get_links():
                    if "uri" in link:
                        links.append(link["uri"])
                
                # Store dimensions
                metadata["page_dimensions"].append({
                    "width": page.rect.width,
                    "height": page.rect.height
                })
            
            # 2. Use pdfplumber for backup/better table extraction if needed in future
            # For now, just ensuring text completeness
            if not raw_text.strip():
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    for page in pdf.pages:
                        raw_text += (page.extract_text() or "") + "\n"
            
            doc.close()
            
            logger.info(f"Successfully extracted PDF: {metadata['page_count']} pages")
            
            return {
                "raw_text": raw_text,
                "metadata": metadata,
                "links": list(set(links))
            }

        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise Exception(f"PDF extraction failed: {str(e)}")
