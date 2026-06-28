import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, "networking_assistant.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# NLP Model configurations
NLP_THEME_MODEL = "distilbert-base-uncased"
NLP_GENERATOR_MODEL = "gpt2"

# Wikipedia client configuration
WIKI_USER_AGENT = "PersonalizedNetworkingAssistant/1.0 (contact@example.com)"
