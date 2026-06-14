import fitz  # PyMuPDF
from typing import Dict, Any, List
from loguru import logger
import os

class LayoutExtractor:
    def __init__(self):
        pass

    async def extract_layout(self, file_path: str) -> Dict[str, Any]:
        """
        Analyzes PDF layout and extracts structural metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        logger.info(f"Extracting layout from: {file_path}")
        
        doc = fitz.open(file_path)
        metadata = {
            "page": {
                "width": 0,
                "height": 0,
                "page_count": len(doc)
            },
            "styles": {},
            "margins": {"top": 0, "bottom": 0, "left": 0, "right": 0},
            "elements": [],
            "sections": []
        }

        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect
            metadata["page"]["width"] = rect.width
            metadata["page"]["height"] = rect.height

            # Extract blocks with detailed formatting
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b["type"] == 0:  # text block
                    block_text = ""
                    block_spans = []
                    for line in b["lines"]:
                        for span in line["spans"]:
                            style_key = f"{span['font']}_{span['size']}_{span['color']}"
                            if style_key not in metadata["styles"]:
                                metadata["styles"][style_key] = {
                                    "font": span["font"],
                                    "size": span["size"],
                                    "color": f"#{span['color']:06x}",
                                    "flags": span["flags"]
                                }
                            
                            block_text += span["text"] + " "
                            block_spans.append({
                                "text": span["text"],
                                "bbox": span["bbox"],
                                "style": style_key
                            })
                    
                    metadata["elements"].append({
                        "text": block_text.strip(),
                        "bbox": b["bbox"],
                        "spans": block_spans
                    })

        doc.close()
        return metadata
