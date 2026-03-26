import os
from dotenv import load_dotenv

load_dotenv()

# Groq — free tier, fast inference
GROQ_API_KEY  = os.getenv("GROQ_API_KEY")
GROQ_MODEL    = "llama3-8b-8192"       # free, fast — swap to llama3-70b-8192 for higher quality

JIRA_BASE_URL     = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL        = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN    = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY  = os.getenv("JIRA_PROJECT_KEY", "QA")

APP_BASE_URL      = os.getenv("APP_BASE_URL", "https://saucedemo.com")

MAX_SELF_HEAL_RETRIES = 2