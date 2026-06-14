from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any
import os

class TemplateEngine:
    """
    Renders optimized resume JSON into ATS-friendly HTML.
    """
    
    def __init__(self, template_dir: str = "app/templates"):
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render_resume(self, resume_json: Dict[str, Any], template_name: str = "ats_template.html") -> str:
        """
        Renders the resume using the specified template.
        """
        # Deep copy and ensure all required fields exist
        safe_resume = {
            "contact": resume_json.get("contact") or {
                "full_name": "",
                "email": "",
                "phone": "",
                "location": ""
            },
            "links": resume_json.get("links") or {},
            "summary": resume_json.get("summary") or "",
            "skills": resume_json.get("skills") or [],
            "experience": resume_json.get("experience") or [],
            "projects": resume_json.get("projects") or [],
            "education": resume_json.get("education") or [],
            "certifications": resume_json.get("certifications") or [],
            "achievements": resume_json.get("achievements") or [],
            "languages": resume_json.get("languages") or [],
        }
        
        # Ensure contact is a dict with defaults
        if not isinstance(safe_resume.get("contact"), dict):
            safe_resume["contact"] = {
                "full_name": "",
                "email": "",
                "phone": "",
                "location": ""
            }
        else:
            # Fill in missing contact fields
            safe_resume["contact"] = {
                "full_name": safe_resume["contact"].get("full_name") or "",
                "email": safe_resume["contact"].get("email") or "",
                "phone": safe_resume["contact"].get("phone") or "",
                "location": safe_resume["contact"].get("location") or "",
            }
        
        # Ensure links is a dict
        if not isinstance(safe_resume.get("links"), dict):
            safe_resume["links"] = {}
        
        template = self.env.get_template(template_name)
        return template.render(resume=safe_resume)

    def render_custom_template(self, template_html: str, template_css: str, resume_json: Dict[str, Any]) -> str:
        """
        Renders a custom HTML template with injected CSS and resume data.
        """
        from jinja2 import Template
        
        # Deep copy and ensure all required fields exist
        safe_resume = {
            "contact": resume_json.get("contact") or {
                "full_name": "",
                "email": "",
                "phone": "",
                "location": ""
            },
            "links": resume_json.get("links") or {},
            "summary": resume_json.get("summary") or "",
            "skills": resume_json.get("skills") or [],
            "experience": resume_json.get("experience") or [],
            "projects": resume_json.get("projects") or [],
            "education": resume_json.get("education") or [],
            "certifications": resume_json.get("certifications") or [],
            "achievements": resume_json.get("achievements") or [],
            "languages": resume_json.get("languages") or [],
        }
        
        # Ensure contact is a dict with defaults
        if not isinstance(safe_resume.get("contact"), dict):
            safe_resume["contact"] = {
                "full_name": "",
                "email": "",
                "phone": "",
                "location": ""
            }
        else:
            # Fill in missing contact fields
            safe_resume["contact"] = {
                "full_name": safe_resume["contact"].get("full_name") or "",
                "email": safe_resume["contact"].get("email") or "",
                "phone": safe_resume["contact"].get("phone") or "",
                "location": safe_resume["contact"].get("location") or "",
            }
        
        # Ensure links is a dict
        if not isinstance(safe_resume.get("links"), dict):
            safe_resume["links"] = {}
        
        template = Template(template_html)
        # Generated templates historically used top-level fields such as
        # `contact` while newer templates use `resume.contact`. Support both.
        return template.render(
            resume=safe_resume,
            template_css=template_css,
            **safe_resume,
        )
