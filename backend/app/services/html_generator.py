from typing import Dict, Any
from jinja2 import Template
from loguru import logger
import lxml.html

class HTMLGenerator:
    def __init__(self):
        pass

    async def generate_html(self, template_html: str, data: Dict[str, Any]) -> str:
        """
        Renders the Jinja2 template with provided data.
        """
        logger.info("Generating HTML from template...")
        try:
            template = Template(template_html)
            rendered_html = template.render(**data)
            
            # Basic validation using lxml
            lxml.html.fromstring(rendered_html)
            
            return rendered_html
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            raise Exception(f"Failed to generate valid HTML: {str(e)}")

    def validate_html(self, html_content: str) -> bool:
        try:
            lxml.html.fromstring(html_content)
            return True
        except Exception:
            return False
