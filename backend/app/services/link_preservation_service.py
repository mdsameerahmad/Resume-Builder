from typing import Dict, Any, List
from loguru import logger

class LinkPreservationService:
    """
    Guarantees all original hyperlinks remain unchanged during optimization.
    """
    
    REQUIRED_LINKS = ["linkedin", "github", "portfolio", "leetcode", "gfg", "website"]

    def preserve_links(self, original_links: Dict[str, Any], optimized_links: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merges original links back into optimized structure to prevent loss.
        """
        preserved = {}
        for key in self.REQUIRED_LINKS:
            # Always prioritize the original link if it exists
            original_val = original_links.get(key)
            if original_val:
                preserved[key] = original_val
            else:
                # Keep whatever the optimizer might have found (if any)
                preserved[key] = optimized_links.get(key, "")
        
        logger.info(f"Preserved links: {list(preserved.keys())}")
        return preserved

class ContactPreservationService:
    """
    Guarantees original contact information remains unchanged.
    """
    
    REQUIRED_FIELDS = ["full_name", "email", "phone", "location"]

    def preserve_contact(self, original_contact: Dict[str, Any], optimized_contact: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensures contact details are not hallucinated or modified.
        """
        preserved = {}
        for field in self.REQUIRED_FIELDS:
            preserved[field] = original_contact.get(field, optimized_contact.get(field, ""))
            
        logger.info(f"Preserved contact info for: {preserved.get('full_name')}")
        return preserved
