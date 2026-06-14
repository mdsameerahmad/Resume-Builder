class TechnologyMapper:
    """
    Maps technologies to their respective families/ecosystems.
    """
    FAMILY_MAPPING = {
        "Python Ecosystem": ["Python", "FastAPI", "Flask", "Django", "Celery", "Pandas", "NumPy"],
        "Java Ecosystem": ["Java", "Spring Boot", "Spring MVC", "Spring Security", "Hibernate", "Maven"],
        "Node Ecosystem": ["Node.js", "Express.js", "NestJS", "npm", "yarn"],
        "Cloud Ecosystem": ["AWS", "Azure", "GCP", "CloudWatch", "EC2", "S3", "Amplify", "Firebase"],
        "DevOps Ecosystem": ["Docker", "CI/CD", "GitHub Actions", "Kubernetes", "Terraform", "Jenkins"],
        "Frontend Ecosystem": ["React", "React.js", "Vue.js", "Angular", "Tailwind CSS", "HTML", "CSS"]
    }

    @classmethod
    def get_family(cls, technology: str) -> list:
        for family, techs in cls.FAMILY_MAPPING.items():
            if any(t.lower() == technology.lower() for t in techs):
                return techs
        return []

    @classmethod
    def is_same_family(cls, tech1: str, tech2: str) -> bool:
        for techs in cls.FAMILY_MAPPING.values():
            techs_lower = [t.lower() for t in techs]
            if tech1.lower() in techs_lower and tech2.lower() in techs_lower:
                return True
        return False
