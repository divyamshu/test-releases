import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

# Configuration from environment variables
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
GITHUB_API_BASE_URL = os.getenv("GITHUB_API_BASE_URL")
# Specific Repository Configuration
GITHUB_OWNER=os.getenv("GITHUB_OWNER")
GITHUB_REPO=os.getenv("GITHUB_REPO")
GITHUB_FILE_PATH=os.getenv("GITHUB_FILE_PATH")
# FastAPI Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
EXPECTED_ENV_KEYS = os.getenv("EXPECTED_ENV_KEYS")

# Load environment variables from .env file
load_dotenv()
