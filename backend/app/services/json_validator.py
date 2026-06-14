import json
import re
from jsonschema import validate, ValidationError
from typing import Any, Dict
from loguru import logger

class InvalidAIJsonError(ValueError):
    pass

class JsonValidator:
    def __init__(self):
        self.schema = {
            "type": "object",
            "properties": {
                "contact": {"type": "object"},
                "links": {"type": "object"},
                "professional_summary": {"type": "string"},
                "skills": {"type": "array"},
                "projects": {"type": "array"},
                "experience": {"type": "array"},
                "education": {"type": "array"},
                "certifications": {"type": "array"},
                "achievements": {"type": "array"},
                "languages": {"type": "array"}
            },
            "required": ["contact", "links", "skills", "projects", "experience", "education"]
        }

    def validate_master_resume(self, data: Dict[str, Any]) -> bool:
        try:
            validate(instance=data, schema=self.schema)
            return True
        except ValidationError as e:
            logger.error(f"JSON Schema Validation Error: {e.message}")
            return False
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            return False

    def clean_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Cleans Gemini's response to ensure it's valid JSON.
        Removes markdown code blocks if present.
        Ensures all fields are strings or lists, not null.
        """
        cleaned = response_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        # Ignore any prose around the JSON object.
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end > start:
            cleaned = cleaned[start:end + 1]
        
        try:
            data = json.loads(cleaned.strip())
            return self._ensure_no_nulls(data)
        except json.JSONDecodeError as e:
            # Gemini occasionally emits JavaScript-like JSON despite requesting
            # application/json. Repair the common safe cases before retrying AI.
            repaired = re.sub(r",\s*([}\]])", r"\1", cleaned)
            repaired = re.sub(
                r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)',
                r'\1"\2"\3',
                repaired,
            )
            try:
                data = json.loads(repaired)
                logger.warning("Repaired malformed JSON returned by AI")
                return self._ensure_no_nulls(data)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from Gemini: {e}")
                raise InvalidAIJsonError("Invalid JSON response from AI") from e

    def _ensure_no_nulls(self, data: Any) -> Any:
        """
        Recursively replaces null values with empty strings or lists.
        """
        if data is None:
            return ""
        if isinstance(data, dict):
            return {k: self._ensure_no_nulls(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self._ensure_no_nulls(i) for i in data]
        return data
