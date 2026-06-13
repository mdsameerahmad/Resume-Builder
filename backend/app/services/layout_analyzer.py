from typing import Dict, Any, List
from loguru import logger

class LayoutAnalyzer:
    def __init__(self):
        self.section_keywords = {
            "contact": ["contact", "email", "phone", "location", "address"],
            "summary": ["summary", "professional summary", "objective", "profile"],
            "skills": ["skills", "technical skills", "core competencies", "expertise"],
            "experience": ["experience", "work experience", "employment history", "professional experience"],
            "projects": ["projects", "academic projects", "personal projects", "key projects"],
            "education": ["education", "academic background", "qualification"],
            "certifications": ["certifications", "licenses", "courses"],
            "achievements": ["achievements", "honors", "awards"],
            "languages": ["languages"]
        }

    async def analyze_sections(self, layout_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detects sections and their hierarchy/ordering based on extracted elements.
        """
        logger.info("Analyzing layout sections and hierarchy...")
        
        elements = layout_metadata.get("elements", [])
        sections = []
        current_section = None
        
        # Simple heuristic: look for headers (usually larger font or bold)
        avg_font_size = sum(e["size"] for e in elements) / len(elements) if elements else 10
        
        for i, element in enumerate(elements):
            text = element["text"].lower().strip()
            is_header = False
            
            # Check if text matches any section keywords and is "header-like"
            for section_type, keywords in self.section_keywords.items():
                if any(kw == text or kw in text for kw in keywords):
                    # Header heuristic: Larger than average or bold flag (flags & 2)
                    if element["size"] > avg_font_size or (element["flags"] & 2):
                        is_header = True
                        sections.append({
                            "type": section_type,
                            "title": element["text"],
                            "bbox": element["bbox"],
                            "font": element["font"],
                            "size": element["size"],
                            "elements_index": i
                        })
                        break
        
        # Determine order
        section_order = [s["type"] for s in sections]
        
        return {
            "sections": sections,
            "section_order": section_order,
            "hierarchy": "single_column" if layout_metadata["page"]["width"] < 1000 else "multi_column"
        }
