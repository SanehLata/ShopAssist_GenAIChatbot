import os
from pathlib import Path
from dotenv import load_dotenv

# -------------------------------------------------
#           Project Root & Load .env
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# -------------------------------------------------
#                   Paths
# -------------------------------------------------
FAQS_PATH = BASE_DIR / "app/resources/faq_data.csv"
DB_PATH = BASE_DIR / "app/resources/etsy_products.db"

# -------------------------------------------------
#               API keys & Models
# -------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

HF_TOKEN = os.getenv("HF_TOKEN")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
OPENAI_API_MODEL=os.getenv("gpt-4o")

# -------------------------------------------------
#           Validate critical keys
# -------------------------------------------------
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set in .env")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not set in .env")
