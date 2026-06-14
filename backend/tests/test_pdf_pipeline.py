import asyncio
import os
import sys
from uuid import UUID

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.compression.page_optimizer import PageOptimizer
from app.services.rendering.template_engine import TemplateEngine
from app.services.rendering.pdf_generator import PDFGenerator

async def test_full_pipeline():
    # Mock optimized resume JSON
    mock_resume = {
        "contact": {"full_name": "John Doe", "location": "New York, NY", "phone": "123-456-7890", "email": "john@example.com"},
        "links": {"linkedin": "https://linkedin.com/in/johndoe", "github": "https://github.com/johndoe"},
        "summary": "Experienced Software Engineer with a strong background in developing scalable web applications using modern technologies. Proven track record of delivering high-quality code and optimizing system performance.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "CI/CD", "React", "JavaScript", "HTML", "CSS", "Git", "Agile"],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Senior Developer",
                "duration": "2020 - Present",
                "responsibilities": [
                    "Lead the development of a microservices-based architecture using FastAPI and PostgreSQL.",
                    "Implemented CI/CD pipelines using GitHub Actions to automate deployment to AWS.",
                    "Optimized database queries, resulting in a 30% reduction in response time.",
                    "Mentored junior developers and conducted code reviews to ensure code quality.",
                    "Collaborated with cross-functional teams to define project requirements and timelines."
                ]
            }
        ],
        "projects": [
            {
                "title": "E-commerce Platform",
                "technologies": ["Python", "Django", "React"],
                "achievements": [
                    "Built a full-featured e-commerce platform with user authentication and payment integration.",
                    "Designed a responsive UI using React and Tailwind CSS for a seamless user experience.",
                    "Integrated Stripe API for secure and efficient payment processing."
                ]
            }
        ],
        "education": [{"institution": "State University", "degree": "B.S. in Computer Science", "year": "2019"}],
        "certifications": ["AWS Certified Solutions Architect", "Professional Scrum Master"]
    }

    print("Step 1: Testing Page Compression...")
    optimizer = PageOptimizer()
    optimized = optimizer.optimize_layout(mock_resume)
    print("Compression successful.")

    print("Step 2: Testing HTML Rendering...")
    renderer = TemplateEngine()
    html = renderer.render_resume(optimized)
    print(f"HTML rendered. Length: {len(html)}")

    print("Step 3: Testing PDF Generation (requires Playwright)...")
    pdf_gen = PDFGenerator()
    output_path = "tests/test_output.pdf"
    os.makedirs("tests", exist_ok=True)
    
    success = await pdf_gen.generate_pdf(html, output_path)
    if success:
        print(f"PDF generated successfully at {output_path}")
    else:
        print("PDF generation failed.")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
