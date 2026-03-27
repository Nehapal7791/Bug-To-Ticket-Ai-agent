import os
from dotenv import load_dotenv

load_dotenv()

# Groq — free tier, fast inference
GROQ_API_KEY  = os.getenv("GROQ_API_KEY")
GROQ_MODEL    = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

JIRA_BASE_URL     = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL        = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN    = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY  = os.getenv("JIRA_PROJECT_KEY", "QA")

APP_BASE_URL      = os.getenv("APP_BASE_URL", "https://qa.sdet360.ai")
APP_VERTICAL_NAME = os.getenv("APP_VERTICAL_NAME", "Alpha")
APP_PROJECT_NAME  = os.getenv("APP_PROJECT_NAME", "AI.SDET360")

MAX_SELF_HEAL_RETRIES = 2