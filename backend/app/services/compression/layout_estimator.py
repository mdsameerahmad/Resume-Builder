from typing import Dict, Any, List
import math

class LayoutEstimator:
    """
    Predicts page overflow before PDF generation based on content length in points (pt).
    A4 is 595.28pt x 841.89pt.
    """
    
    # Heuristic characters per line for A4 at standard font size
    CHARS_PER_LINE = 90
    LINE_HEIGHT_PT = 15.6 # ~5.5mm
    PAGE_HEIGHT_PT = 841.89
    MARGIN_PT = 56.69 # ~20mm
    AVAILABLE_HEIGHT_PT = PAGE_HEIGHT_PT - MARGIN_PT

    def estimate_height(self, resume_json: Dict[str, Any]) -> Dict[str, float]:
        """
        Estimates the height of each section in pt.
        """
        heights = {
            "header": 70.0, # Contact info and links
            "summary": self._estimate_text_height(resume_json.get("summary", ""), weight=1.1),
            "skills": self._estimate_list_height(resume_json.get("skills", []), items_per_row=3),
            "projects": self._estimate_complex_list_height(resume_json.get("projects", []), bullet_key="achievements"),
            "experience": self._estimate_complex_list_height(resume_json.get("experience", []), bullet_key="responsibilities"),
            "education": self._estimate_list_height(resume_json.get("education", []), items_per_row=1),
            "certifications": self._estimate_list_height(resume_json.get("certifications", []), items_per_row=2)
        }
        
        total_height = sum(heights.values())
        return {
            "total_height": total_height,
            "is_overflow": total_height > self.AVAILABLE_HEIGHT_PT,
            "overflow_amount": max(0, total_height - self.AVAILABLE_HEIGHT_PT),
            "sections": heights
        }

    def _estimate_text_height(self, text: str, weight: float = 1.0) -> float:
        if not text: return 0
        lines = math.ceil(len(text) / self.CHARS_PER_LINE)
        return lines * self.LINE_HEIGHT_PT * weight

    def _estimate_list_height(self, items: List[Any], items_per_row: int = 1) -> float:
        if not items: return 0
        rows = math.ceil(len(items) / items_per_row)
        return rows * self.LINE_HEIGHT_PT + 14 # +14 for section title

    def _estimate_complex_list_height(self, items: List[Dict[str, Any]], bullet_key: str) -> float:
        if not items: return 0
        height = 14 # Title
        for item in items:
            height += 17 # Header (Title, Role, Date)
            bullets = item.get(bullet_key, [])
            for bullet in bullets:
                height += self._estimate_text_height(bullet)
        return height
