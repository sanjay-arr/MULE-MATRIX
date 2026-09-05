import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mule Matrix API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Neo4j configuration
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password") # Default for local dev only

    class Config:
        case_sensitive = True

settings = Settings()
