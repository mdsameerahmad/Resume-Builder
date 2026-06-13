import re
from typing import Dict, Optional
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from loguru import logger

class ContactExtractor:
    def __init__(self):
        self.email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        # Simple phone pattern for initial regex search
        self.phone_regex = r'(\+?\d[\d\-\(\) ]{8,}\d)'
        
        # Location indicators
        self.location_indicators = [
            "Bengaluru", "Bangalore", "Mumbai", "Delhi", "Gurgaon", "Pune", "Hyderabad", "Chennai", 
            "Noida", "Kolkata", "Ahmedabad", "California", "New York", "London", "India", "USA", "UK"
        ]

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extracts contact info (email, phone, name, location) from text.
        """
        contact_info = {
            "name": None,
            "email": None,
            "phone": None,
            "location": None
        }
        
        # 1. Extract Email
        emails = re.findall(self.email_pattern, text)
        for email in emails:
            try:
                # Basic validation
                validate_email(email, check_deliverability=False)
                contact_info["email"] = email.strip()
                break
            except EmailNotValidError:
                continue
        
        # 2. Extract Phone
        # Try regex first to find potential candidates
        phone_candidates = re.findall(self.phone_regex, text)
        for candidate in phone_candidates:
            try:
                # Use phonenumbers library for robust validation
                # We try IN (India) first as a common default, but phonenumbers handles + prefixes globally
                parsed = phonenumbers.parse(candidate, "IN")
                if phonenumbers.is_valid_number(parsed):
                    contact_info["phone"] = phonenumbers.format_number(
                        parsed, phonenumbers.PhoneNumberFormat.E164
                    )
                    break
            except Exception:
                continue

        # 3. Extract Name (Heuristic: usually first few lines, capitalized)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Often the first non-empty line is the name
            first_line = lines[0]
            if len(first_line.split()) <= 4 and all(word[0].isupper() for word in first_line.split() if word[0].isalpha()):
                contact_info["name"] = first_line

        # 4. Extract Location (Simple keyword matching)
        for city in self.location_indicators:
            if re.search(r'\b' + re.escape(city) + r'\b', text, re.IGNORECASE):
                contact_info["location"] = city
                break
                
        logger.debug(f"Extracted contact info: {contact_info}")
        return contact_info
