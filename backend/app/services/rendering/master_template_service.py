import re
from typing import Dict, Any, List
from loguru import logger
import jinja2

class MasterTemplateService:
    """
    Creates a high-fidelity Jinja2 template from extracted PDF layout metadata.
    """
    
    SECTION_MAPPING = {
        "summary": ["summary", "profile", "objective", "about me"],
        "experience": ["experience", "work history", "employment", "professional background"],
        "education": ["education", "academic", "qualifications"],
        "skills": ["skills", "technical skills", "expertise", "competencies"],
        "projects": ["projects", "personal projects", "academic projects"],
        "certifications": ["certifications", "certificates", "licenses"],
        "achievements": ["achievements", "honors", "awards"],
        "languages": ["languages"],
    }

    def __init__(self):
        pass

    def create_template(self, layout_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes layout metadata to identify sections and generate HTML/CSS templates.
        """
        logger.info("Creating master template from layout metadata...")
        
        styles = layout_metadata.get("styles", {})
        elements = layout_metadata.get("elements", [])
        
        # 1. Generate CSS from detected styles
        css_rules = []
        style_map = {}
        for i, (key, style) in enumerate(styles.items()):
            class_name = f"style-{i}"
            style_map[key] = class_name
            
            # Basic font mapping (improve as needed)
            font_family = "Arial, sans-serif"
            if "bold" in style["font"].lower():
                weight = "bold"
            else:
                weight = "normal"
                
            css_rules.append(f".{class_name} {{ font-family: '{style['font']}', {font_family}; font-size: {style['size']}pt; color: {style['color']}; font-weight: {weight}; }}")
        
        css_template = "\n".join(css_rules)
        
        # 2. Identify Sections in Elements
        sections = self._identify_sections(elements)
        
        # 3. Build HTML Template with Jinja2 placeholders
        html_template = self._build_html_skeleton(sections, style_map, layout_metadata)
        
        return {
            "template_html": html_template,
            "template_css": css_template,
            "layout_metadata": layout_metadata,
            "section_order": [s["type"] for s in sections]
        }

    def _identify_sections(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Groups elements into logical resume sections.
        """
        identified_sections = []
        current_section = {"type": "header", "elements": []}
        
        for el in elements:
            text = el["text"].lower().strip()
            found_new_section = False
            
            # Check if this element is a section header
            if len(text.split()) < 4:
                for sec_type, keywords in self.SECTION_MAPPING.items():
                    if any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in keywords):
                        if current_section["elements"] or "title" in current_section:
                            identified_sections.append(current_section)
                        current_section = {"type": sec_type, "title": el["text"], "elements": [], "header_style": el["spans"][0]["style"] if el["spans"] else None}
                        found_new_section = True
                        break
            
            if not found_new_section:
                current_section["elements"].append(el)
        
        if current_section["elements"] or "title" in current_section:
            identified_sections.append(current_section)
            
        return identified_sections

    def _build_html_skeleton(self, sections: List[Dict[str, Any]], style_map: Dict[str, str], layout_metadata: Dict[str, Any]) -> str:
        """
        Creates the HTML with Jinja2 placeholders for each section.
        """
        width = layout_metadata["page"]["width"]
        
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<style>",
            "@page { size: var(--page-width) var(--page-height); margin: 0; }",
            "html, body { margin: 0; padding: 0; }",
            "body { font-family: Helvetica, Arial, sans-serif; font-size: 7.7pt; line-height: 1.12; color: #000; }",
            f".resume-container {{ box-sizing: border-box; width: {width}pt; padding: 26pt 34pt; margin: 0; }}",
            ".section-header { text-align: center; margin-bottom: 5pt; }",
            ".section-header h1 { margin: 0 0 2pt; font-size: 17.5pt; color: #1a1a2e; }",
            ".section-header p { margin: 1pt 0; font-size: 7.2pt; }",
            ".section-header a { color: #1a5575; text-decoration: none; }",
            "h2 { margin: 4pt 0 2pt; padding-bottom: 1pt; border-bottom: .7pt solid #1a5575; font-size: 8.5pt; color: #1a5575; line-height: 1; }",
            "p { margin: 1pt 0; }",
            "ul { margin: 1pt 0 2pt 12pt; padding: 0; }",
            "li { margin: 0; padding: 0; }",
            ".job-item, .project-item, .education-item { margin-bottom: 2pt; break-inside: avoid; }",
            ".item-heading { display: flex; justify-content: space-between; gap: 8pt; font-weight: bold; }",
            ".item-heading span:last-child { text-align: right; font-weight: normal; }",
            ".inline-list { margin: 1pt 0; }",
            "{{ template_css }}",
            "</style>",
            "</head>",
            "<body>",
            "<div class='resume-container'>"
        ]

        for sec in sections:
            sec_type = sec["type"]
            
            if sec_type == "header":
                html.append("<div class='section-header'>")
                html.append("  <h1>{{ resume.contact.full_name }}</h1>")
                html.append("  <p>{% if resume.contact.email %}{{ resume.contact.email }}{% endif %}{% if resume.contact.phone %} | {{ resume.contact.phone }}{% endif %}{% if resume.contact.location %} | {{ resume.contact.location }}{% endif %}</p>")
                # Add all preserved links
                html.append("  <p>{% set link_items = [] %}")
                html.append("    {% for label, url in resume.links.items() %}{% if url %}{% set _ = link_items.append((label, url)) %}{% endif %}{% endfor %}")
                html.append("    {% for label, url in link_items %}<a href='{{ url }}'>{% if label == 'github' %}GitHub{% elif label == 'linkedin' %}LinkedIn{% elif label == 'leetcode' %}LeetCode{% elif label == 'gfg' %}GFG{% else %}{{ label|replace('_', ' ')|title }}{% endif %}</a>{% if not loop.last %} | {% endif %}{% endfor %}")
                html.append("  </p>")
                html.append("</div>")
            
            elif sec_type == "summary":
                html.append("<div class='section-summary'>")
                if "title" in sec:
                    style_class = style_map.get(sec["header_style"], "")
                    html.append(f"  <h2 class='{style_class}'>{sec['title']}</h2>")
                html.append("  <p>{{ resume.summary }}</p>")
                html.append("</div>")
                
            elif sec_type == "skills":
                html.append("<div class='section-skills'>")
                if "title" in sec:
                    style_class = style_map.get(sec["header_style"], "")
                    html.append(f"  <h2 class='{style_class}'>{sec['title']}</h2>")
                html.append("  <p>{% for skill in resume.skills %}{{ skill }}{% if not loop.last %}, {% endif %}{% endfor %}</p>")
                html.append("</div>")

            elif sec_type == "experience":
                html.append("<div class='section-experience'>")
                if "title" in sec:
                    style_class = style_map.get(sec["header_style"], "")
                    html.append(f"  <h2 class='{style_class}'>{sec['title']}</h2>")
                html.append("  {% for job in resume.experience %}")
                html.append("    <div class='job-item'>")
                html.append("      <div class='item-heading'>")
                html.append("        <span>{{ job.role }}{% if job.company %} - {{ job.company }}{% endif %}</span>")
                html.append("        <span>{{ job.duration }}</span>")
                html.append("      </div>")
                html.append("      <ul>")
                html.append("        {% for bullet in job.responsibilities %}")
                html.append("          <li>{{ bullet }}</li>")
                html.append("        {% endfor %}")
                html.append("      </ul>")
                html.append("    </div>")
                html.append("  {% endfor %}")
                html.append("</div>")

            elif sec_type == "projects":
                html.append("<div class='section-projects'>")
                if "title" in sec:
                    style_class = style_map.get(sec["header_style"], "")
                    html.append(f"  <h2 class='{style_class}'>{sec['title']}</h2>")
                html.append("  {% for project in resume.projects %}")
                html.append("    <div class='project-item'>")
                html.append("      <div class='item-heading'>")
                html.append("        <span>{{ project.title }}</span>")
                html.append("        <span>{{ project.technologies|join(', ') }}</span>")
                html.append("      </div>")
                html.append("      {% if project.description %}<p>{{ project.description }}</p>{% endif %}")
                html.append("      <ul>")
                html.append("        {% for bullet in project.achievements %}")
                html.append("          <li>{{ bullet }}</li>")
                html.append("        {% endfor %}")
                html.append("      </ul>")
                html.append("    </div>")
                html.append("  {% endfor %}")
                html.append("</div>")

            elif sec_type == "education":
                html.append("<div class='section-education'>")
                if "title" in sec:
                    style_class = style_map.get(sec["header_style"], "")
                    html.append(f"  <h2 class='{style_class}'>{sec['title']}</h2>")
                html.append("  {% for edu in resume.education %}")
                html.append("    <div class='education-item'>")
                html.append("      <div class='item-heading'><span>{{ edu.degree }}{% if edu.institution %} - {{ edu.institution }}{% endif %}{% if edu.cgpa %} | {{ edu.cgpa }}{% endif %}</span><span>{{ edu.year }}</span></div>")
                html.append("    </div>")
                html.append("  {% endfor %}")
                html.append("</div>")

            elif sec_type in ("certifications", "achievements", "languages"):
                field = sec_type
                html.append(f"<div class='section-{field}'>")
                if "title" in sec:
                    style_class = style_map.get(sec["header_style"], "")
                    html.append(f"  <h2 class='{style_class}'>{sec['title']}</h2>")
                html.append(f"  <ul>{{% for item in resume.{field} %}}<li>{{{{ item }}}}</li>{{% endfor %}}</ul>")
                html.append("</div>")

        # Optimized content may contain sections absent from the source layout.
        # Append them compactly so valid resume information is never dropped.
        identified = {section["type"] for section in sections}
        for field, title in (
            ("certifications", "CERTIFICATIONS"),
            ("achievements", "ACHIEVEMENTS"),
            ("languages", "LANGUAGES"),
        ):
            if field not in identified:
                html.append(f"{{% if resume.{field} %}}<div class='section-{field}'><h2>{title}</h2><ul>{{% for item in resume.{field} %}}<li>{{{{ item }}}}</li>{{% endfor %}}</ul></div>{{% endif %}}")

        html.append("</div>")
        html.append("</body>")
        html.append("</html>")
        
        return "\n".join(html)
