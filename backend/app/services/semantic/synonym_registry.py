class SynonymRegistry:
    """
    Central registry for synonyms and equivalent terms.
    """
    SYNONYMS = {
        "REST API": [
            "REST APIs", "RESTful API", "RESTful APIs", "RESTful API Design",
            "API Development", "FastAPI", "Spring REST", "Express API"
        ],
        "API Development": [
            "REST API", "REST APIs", "RESTful API Design", "FastAPI",
            "Spring Boot APIs", "Backend Services", "APIs"
        ],
        "APIs": [
            "REST API", "REST APIs", "RESTful API Design", "FastAPI",
            "Spring Boot APIs", "Backend Services", "API Development"
        ],
        "DevOps": [
            "Docker", "CI/CD", "AWS", "CloudWatch", "Deployment Automation",
            "Containerization", "Infrastructure Automation"
        ],
        "Database Management": [
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "Oracle DB",
            "Database Engineering", "Query Optimization"
        ],
        "Automation": [
            "Workflow Automation", "Celery", "Task Scheduling",
            "Pipeline Automation", "Background Jobs"
        ],
        "Testing": [
            "Unit Testing", "Integration Testing", "API Testing",
            "Postman Testing", "Test Automation"
        ],
        "JavaScript": ["JS", "Node.js", "React.js", "Vue.js"],
        "Cloud Platform": ["AWS", "Azure", "GCP", "Cloud Services"]
    }

    @classmethod
    def get_synonyms(cls, term: str) -> list:
        return cls.SYNONYMS.get(term, [])
