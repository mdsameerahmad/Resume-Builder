import re
from typing import Dict, List, Optional
from loguru import logger

class LinkExtractor:
    def __init__(self):
        # Regex patterns for different platforms
        self.patterns = {
            "linkedin": r"(https?://(?:www\.)?linkedin\.com/in/[\w\-\_%/]+)",
            "github": r"(https?://(?:www\.)?github\.com/[\w\-\_]+)",
            "leetcode": r"(https?://(?:www\.)?leetcode\.com/[\w\-\_]+)",
            "gfg": r"(https?://(?:auth\.)?geeksforgeeks\.org/user/[\w\-\_]+)",
            "portfolio": r"(https?://(?:www\.)?[\w\-\.]+\.(?:me|io|com|net|org)(?:/[\w\-\_]*)?)",
            "youtube": r"(https?://(?:www\.)?(?:youtube\.com/channel/|youtube\.com/c/|youtube\.com/user/|youtube\.com/@)[\w\-\_]+)",
        }
        
        # General URL pattern
        self.url_pattern = r"(https?://[^\s<>\"#]+[^\s<>\"#.])"

    def extract_links(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts and categorizes links from text.
        """
        extracted = {
            "linkedin": [],
            "github": [],
            "leetcode": [],
            "gfg": [],
            "portfolio": [],
            "youtube": [],
            "other_urls": []
        }
        
        # Find all URLs first
        all_urls = list(set(re.findall(self.url_pattern, text)))
        
        for url in all_urls:
            url = url.strip().rstrip("/.,")
            found = False
            for platform, pattern in self.patterns.items():
                if re.search(pattern, url, re.IGNORECASE):
                    extracted[platform].append(url)
                    found = True
                    break
            
            if not found:
                # Basic check for website/portfolio if not already matched
                if not any(platform in url.lower() for platform in ["linkedin", "github", "leetcode", "geeksforgeeks"]):
                    extracted["other_urls"].append(url)
        
        # Deduplicate and sort
        for key in extracted:
            extracted[key] = sorted(list(set(extracted[key])))
            
        logger.debug(f"Extracted {sum(len(v) for v in extracted.values())} links")
        return extracted
