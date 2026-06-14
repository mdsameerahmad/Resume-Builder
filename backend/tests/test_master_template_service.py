from app.services.rendering.master_template_service import MasterTemplateService
from app.services.rendering.template_engine import TemplateEngine


def test_master_template_renders_complete_resume_content():
    layout = {
        "page": {"width": 612, "height": 792, "page_count": 1},
        "styles": {},
        "elements": [
            {"text": "Header", "bbox": [0, 0, 1, 1], "spans": []},
            {"text": "Professional Summary", "bbox": [0, 0, 1, 1], "spans": []},
            {"text": "Technical Skills", "bbox": [0, 0, 1, 1], "spans": []},
            {"text": "Work Experience", "bbox": [0, 0, 1, 1], "spans": []},
            {"text": "Projects", "bbox": [0, 0, 1, 1], "spans": []},
            {"text": "Education", "bbox": [0, 0, 1, 1], "spans": []},
        ],
    }
    resume = {
        "contact": {"full_name": "Jane Doe", "email": "jane@example.com", "phone": "123", "location": "NY"},
        "links": {"github": "https://github.com/jane"},
        "summary": "Backend engineer",
        "skills": ["Python"],
        "experience": [{"role": "Engineer", "company": "Acme", "duration": "2024", "responsibilities": ["Built APIs"]}],
        "projects": [{"title": "Platform", "description": "Useful platform", "technologies": ["FastAPI"], "achievements": ["Improved speed"]}],
        "education": [{"degree": "BSc", "institution": "College", "cgpa": "9.0", "year": "2023"}],
        "certifications": ["AWS Certified"],
        "achievements": ["Won award"],
        "languages": ["English"],
    }

    template = MasterTemplateService().create_template(layout)
    html = TemplateEngine().render_custom_template(template["template_html"], template["template_css"], resume)

    for expected in ("GitHub", "Useful platform", "9.0", "AWS Certified", "Won award", "English"):
        assert expected in html
