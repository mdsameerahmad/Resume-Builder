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
            "fonts": set(),
            "font_sizes": set(),
            "colors": set(),
            "margins": {"top": 0, "bottom": 0, "left": 0, "right": 0},
            "elements": []
        }

        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect
            metadata["page"]["width"] = rect.width
            metadata["page"]["height"] = rect.height

            # Extract blocks of text with formatting
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b["type"] == 0:  # text block
                    for line in b["lines"]:
                        for span in line["spans"]:
                            metadata["fonts"].add(span["font"])
                            metadata["font_sizes"].add(round(span["size"], 2))
                            # Convert color to hex
                            color = span["color"]
                            metadata["colors"].add(f"#{color:06x}")
                            
                            metadata["elements"].append({
                                "text": span["text"],
                                "bbox": span["bbox"],
                                "font": span["font"],
                                "size": span["size"],
                                "color": f"#{color:06x}",
                                "flags": span["flags"]
                            })

        doc.close()
        
        # Convert sets to lists for JSON serialization
        metadata["fonts"] = list(metadata["fonts"])
        metadata["font_sizes"] = sorted(list(metadata["font_sizes"]))
        metadata["colors"] = list(metadata["colors"])
        
        return metadata
