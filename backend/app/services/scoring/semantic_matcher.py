import re

class SemanticMatcher:
    """
    Intelligent matching engine for skills and keywords (e.g., JS -> JavaScript).
    """
    
    SYNONYMS = {
        "js": ["javascript", "js", "reactjs", "node.js", "nodejs"],
        "javascript": ["js", "javascript"],
        "react": ["react", "reactjs", "react.js"],
        "reactjs": ["react", "reactjs", "react.js"],
        "node": ["node", "nodejs", "node.js"],
        "nodejs": ["node", "nodejs", "node.js"],
        "node.js": ["node", "nodejs", "node.js"],
        "rest api": ["rest api", "rest apis", "restful api", "restful apis", "rest"],
        "rest apis": ["rest api", "rest apis", "restful api", "restful apis", "rest"],
        "github": ["github", "git", "gitlab"],
        "git": ["git", "github", "gitlab"],
        "aws": ["aws", "amazon web services", "amazon"],
        "amazon web services": ["aws", "amazon web services", "amazon"],
        "gcp": ["gcp", "google cloud platform", "google cloud"],
        "google cloud platform": ["gcp", "google cloud platform", "google cloud"],
        "sql": ["sql", "mysql", "postgresql", "sql server"],
        "ml": ["ml", "machine learning"],
        "ai": ["ai", "artificial intelligence"],
        "cicd": ["cicd", "ci/cd", "continuous integration", "continuous deployment"]
    }

    def is_match(self, term1: str, term2: str) -> bool:
        """
        Checks if two terms match semantically.
        """
        t1 = self._normalize(term1)
        t2 = self._normalize(term2)
        
        if t1 == t2:
            return True
            
        # Check synonyms
        if t1 in self.SYNONYMS and t2 in self.SYNONYMS[t1]:
            return True
        if t2 in self.SYNONYMS and t1 in self.SYNONYMS[t2]:
            return True
            
        return False

    def _normalize(self, text: str) -> str:
        # Lowercase, remove special chars, trim
        text = text.lower().strip()
        text = re.sub(r'[^a-z0-9\s\.\/\#]', '', text)
        return text
