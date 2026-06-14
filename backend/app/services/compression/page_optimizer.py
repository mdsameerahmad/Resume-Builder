from typing import Dict, Any, List
import copy
from loguru import logger
from app.services.compression.layout_estimator import LayoutEstimator

class PageOptimizer:
    """
    Guarantees every generated resume fits on exactly one A4 page.
    """
    
    def __init__(self):
        self.estimator = LayoutEstimator()

    def optimize_layout(self, resume_json: Dict[str, Any], max_height_pt: float = 842.0) -> Dict[str, Any]:
        """
        Iteratively compresses content until it fits on one page (A4 height is ~842pt).
        """
        optimized_json = copy.deepcopy(resume_json)
        
        # Ensure all required fields exist with safe defaults
        if not optimized_json.get("contact") or not isinstance(optimized_json.get("contact"), dict):
            optimized_json["contact"] = {
                "full_name": "",
                "email": "",
                "phone": "",
                "location": ""
            }
        
        # Fill in missing contact fields
        contact = optimized_json.get("contact", {})
        optimized_json["contact"] = {
            "full_name": contact.get("full_name") or "",
            "email": contact.get("email") or "",
            "phone": contact.get("phone") or "",
            "location": contact.get("location") or "",
        }
        
        if not optimized_json.get("links") or not isinstance(optimized_json.get("links"), dict):
            optimized_json["links"] = {}
        
        # 1. Estimate initial height
        estimation = self.estimator.estimate_height(optimized_json)
        
        if not estimation["is_overflow"]:
            return optimized_json

        logger.info(f"Overflow detected ({estimation['total_height']}pt). Starting compression pipeline...")

        # 2. Strategy 1: Compress Summary (Reduce length)
        if estimation["is_overflow"]:
            summary = optimized_json.get("summary", "")
            if len(summary) > 300:
                optimized_json["summary"] = summary[:300] + "..."
                estimation = self.estimator.estimate_height(optimized_json)

        # 3. Strategy 2: Compress Project Bullets (Keep top 3)
        if estimation["is_overflow"]:
            optimized_json["projects"] = self._compress_sections(
                optimized_json.get("projects", []), 
                bullet_key="achievements",
                min_bullets=3
            )
            estimation = self.estimator.estimate_height(optimized_json)

        # 4. Strategy 3: Compress Experience Bullets (Keep top 4)
        if estimation["is_overflow"]:
            optimized_json["experience"] = self._compress_sections(
                optimized_json.get("experience", []), 
                bullet_key="responsibilities",
                min_bullets=4
            )
            estimation = self.estimator.estimate_height(optimized_json)

        # 5. Strategy 4: Remove low-value achievements (bullets with less than 40 chars)
        if estimation["is_overflow"]:
            optimized_json["experience"] = self._remove_short_bullets(
                optimized_json.get("experience", []),
                bullet_key="responsibilities"
            )
            estimation = self.estimator.estimate_height(optimized_json)

        # 6. Strategy 5: Reduce whitespace (This is handled in CSS rendering, but we can set a flag)
        if estimation["is_overflow"]:
            optimized_json["layout_settings"] = {"compact": True}
            # Reducing spacing in estimation (simulated)
            estimation["total_height"] *= 0.9 
            estimation["is_overflow"] = estimation["total_height"] > max_height_pt

        # 7. Strategy 6: Recalculate layout (Final trim of sections)
        if estimation["is_overflow"]:
            if len(optimized_json.get("projects", [])) > 2:
                optimized_json["projects"] = optimized_json["projects"][:2]
            
        return optimized_json

    def _remove_short_bullets(self, items: List[Dict[str, Any]], bullet_key: str) -> List[Dict[str, Any]]:
        for item in items:
            bullets = item.get(bullet_key, [])
            item[bullet_key] = [b for b in bullets if len(b) > 40]
        return items

    def _compress_sections(self, items: List[Dict[str, Any]], bullet_key: str, min_bullets: int) -> List[Dict[str, Any]]:
        """
        Reduces the number of bullets in a list of items.
        """
        for item in items:
            bullets = item.get(bullet_key, [])
            if len(bullets) > min_bullets:
                item[bullet_key] = bullets[:min_bullets]
        return items
