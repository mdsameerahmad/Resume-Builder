import json
from jsonschema import validate, ValidationError
from typing import Any, Dict
from loguru import logger

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
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "", 1)
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        
        try:
            data = json.loads(cleaned.strip())
            return self._ensure_no_nulls(data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from Gemini: {e}")
            raise Exception("Invalid JSON response from AI")

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
