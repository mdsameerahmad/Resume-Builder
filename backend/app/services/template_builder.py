from typing import Dict, Any, List
from loguru import logger
from jinja2 import Environment, FileSystemLoader
import os

class TemplateBuilder:
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    async def build_template(self, layout_metadata: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """
        Generates a reusable Jinja2 HTML template based on layout analysis.
        """
        logger.info("Building reusable HTML template...")
        
        # Define placeholders based on Master Resume JSON structure
        placeholders = {
            "contact": {
                "full_name": "{{ contact.full_name }}",
                "email": "{{ contact.email }}",
                "phone": "{{ contact.phone }}",
                "location": "{{ contact.location }}"
            },
            "professional_summary": "{{ professional_summary }}",
            "skills": "{% for skill in skills %}<span class='skill'>{{ skill }}</span>{% if not loop.last %}, {% endif %}{% endfor %}",
            "experience": """
                {% for job in experience %}
                <div class="experience-item">
                    <h3>{{ job.role }} at {{ job.company }}</h3>
                    <p>{{ job.duration }}</p>
                    <ul>
                        {% for resp in job.responsibilities %}
                        <li>{{ resp }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endfor %}
            """,
            "projects": """
                {% for project in projects %}
                <div class="project-item">
                    <h3>{{ project.title }}</h3>
                    <p>{{ project.description }}</p>
                    <p><strong>Tech:</strong> {{ project.technologies|join(', ') }}</p>
                </div>
                {% endfor %}
            """,
            "education": """
                {% for edu in education %}
                <div class="education-item">
                    <h3>{{ edu.degree }}</h3>
                    <p>{{ edu.institution }} ({{ edu.year }})</p>
                </div>
                {% endfor %}
            """
        }

        # Basic HTML skeleton
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Resume Template</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.5;
            margin: 40px;
            color: #333;
            width: {layout_metadata['page']['width']}px;
        }}
        .header {{ text-align: center; margin-bottom: 20px; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ 
            font-size: 1.2em; 
            font-weight: bold; 
            border-bottom: 1px solid #ccc; 
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .experience-item, .project-item, .education-item {{ margin-bottom: 15px; }}
        h3 {{ margin: 0; font-size: 1.1em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{placeholders['contact']['full_name']}</h1>
        <p>{placeholders['contact']['email']} | {placeholders['contact']['phone']} | {placeholders['contact']['location']}</p>
    </div>

    <div class="section">
        <div class="section-title">Professional Summary</div>
        <p>{placeholders['professional_summary']}</p>
    </div>

    <div class="section">
        <div class="section-title">Skills</div>
        <p>{placeholders['skills']}</p>
    </div>

    <div class="section">
        <div class="section-title">Experience</div>
        {placeholders['experience']}
    </div>

    <div class="section">
        <div class="section-title">Projects</div>
        {placeholders['projects']}
    </div>

    <div class="section">
        <div class="section-title">Education</div>
        {placeholders['education']}
    </div>
</body>
</html>
        """
        return html
