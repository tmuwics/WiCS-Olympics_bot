import os
from dotenv import load_dotenv 

#loading the .env file
load_dotenv()
TOKEN = os.getenv("WICS_OLYMPICS_TOKEN")
SHEETDB_URL = os.getenv("SHEETDB_URL")
ALLOWED_CHANNEL_ID = int(os.getenv("ALLOWED_CHANNEL_ID")) if os.getenv("ALLOWED_CHANNEL_ID") else None

POINTS_PER_SUBMIT = 10
POINTS_PER_IG_POST = 5
ROLE_SEPARATOR = " - "
TAG = "#execfound"
ALLOWED_EMAIL_DOMAIN = "@torontomu.ca"

if not SHEETDB_URL:
    raise RuntimeError("SHEETDB_URL is not set. Check your .env file.")
if not TOKEN:
    raise RuntimeError("WICS_OLYMPICS_TOKEN not set")